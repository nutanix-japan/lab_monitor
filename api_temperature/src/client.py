import time
import schedule
import subprocess
import threading
import uuid
from datetime import datetime
from pymongo import MongoClient

import bson.json_util
import fastapi
import json

class TemperatureClient:

  DB_TEMPERATURE = 'api_temperature'
  COL_HOST = 'host_v1'
  COL_TEMPERATURE = 'temperature_v1'

  def __init__(self, host, port, username, password, erase_db=False, auto_collect=True):
    self.client = MongoClient(f'mongodb://{host}:{port}/',
      username=username, password=password)

    if erase_db:
      self.rm_all()
    self.colh = self.client[self.DB_TEMPERATURE][self.COL_HOST]
    self.colt = self.client[self.DB_TEMPERATURE][self.COL_TEMPERATURE]

    if not auto_collect:
      return

    def fun():
      schedule.every().minutes.do(self.job)
      while True:
        schedule.run_pending()
        time.sleep(1)
    threading.Thread(target=fun).start()

  def rm_all(self):
    self.client.drop_database(self.DB_TEMPERATURE)
    self.colh = self.client[self.DB_TEMPERATURE][self.COL_HOST]
    self.colt = self.client[self.DB_TEMPERATURE][self.COL_TEMPERATURE]

  def get_summary(self):
    hosts = self.get_hosts()

    uuid2name = {}
    for host in hosts:
      uuid2name[host['uuid']] = host['name'] 

    # current temperature of all hosts
    for host in hosts:
      result = self.colt.find_one({'host_uuid':host['uuid']}, 
        {'_id': False}, sort=[("timestamp", -1)])
      if result is None:
        host['timestamp'] = 0
        host['temperature'] = 0
      else:
        host['timestamp'] = result['timestamp']
        host['temperature'] = result['temperature']
    hosts.sort(key=lambda x:x['name'])

    # latest
    result = self.colt.find_one({}, {'_id': False}, sort=[("timestamp", -1)])
    if result is None:
      return {
        'hosts':hosts,
        'day_max':0,
        'day_timestamp':0,
        'day_name':'',
        'week_max':0,
        'week_timestamp':0,
        'week_name':'',
        'month_max':0,
        'month_timestamp':0,
        'month_name':'',
      }

    # calc 24h-ago, 1week-ago, 1month-ago
    max_timestamp = result['timestamp']
    month_ago_timestamp = max_timestamp - 60 * 60 * 24 * 31
    week_ago_timestamp = max_timestamp - 60 * 60 * 24 * 7
    day_ago_timestamp = max_timestamp - 60 * 60 * 24

    # get max heat on 3 ranges
    month_result = self.colt.find_one({'timestamp':{"$gt": month_ago_timestamp}},
     {'_id': False}, sort=[("temperature", -1), ("timestamp", -1)])
    week_result = self.colt.find_one({'timestamp':{"$gt": week_ago_timestamp}},
     {'_id': False}, sort=[("temperature", -1), ("timestamp", -1)])
    day_result = self.colt.find_one({'timestamp':{"$gt": day_ago_timestamp}},
     {'_id': False}, sort=[("temperature", -1), ("timestamp", -1)])

    # create return value
    d = {
      'hosts':hosts,
      'day_max':day_result['temperature'],
      'day_timestamp':day_result['timestamp'],
      'day_name':uuid2name[day_result['host_uuid']],
      'week_max':week_result['temperature'],
      'week_timestamp':week_result['timestamp'],
      'week_name':uuid2name[week_result['host_uuid']],
      'month_max':month_result['temperature'],
      'month_timestamp':month_result['timestamp'],
      'month_name':uuid2name[month_result['host_uuid']],
    }
    return d


  def get_hosts(self):
    hosts = get_json(self.colh.find({},{'_id': False}))
    hosts.sort(key=lambda x:x['name'])
    return hosts

  def add_host(self, name, ip):
    name = name.strip()
    ip = ip.strip()
    if self.colh.find({'name':name}).count() >= 1:
      return
    d = {
      'uuid':str(uuid.uuid4()),
      'name':name,
      'ip':ip,
    }
    self.colh.insert_one(d)

  def rm_host(self, host_uuid):
    self.colh.delete_many({'uuid':host_uuid})
    self.colt.delete_many({'host_uuid':host_uuid})

  def get_host_temperatures(self, host_uuid, showing_range='date'):
    result = self.colt.find_one({'host_uuid':host_uuid}, 
      {'_id': False}, sort=[("timestamp", -1)])
    if result is None:
      return []

    max_timestamp = result['timestamp']
    if showing_range == 'month':
      min_timestamp = max_timestamp - 60 * 60 * 24 * 31
    elif showing_range == 'week':
      min_timestamp = max_timestamp - 60 * 60 * 24 * 7
    else:
      min_timestamp = max_timestamp - 60 * 60 * 24

    result = self.colt.find({'host_uuid':host_uuid, 
     'timestamp':{"$gt": min_timestamp}},
     {'_id': False, 'host_uuid': False}).sort([('timestamp', 1)])
    return get_json(result)

  def add_host_temperature(self, host_uuid, datetime_iso9601, temperature):
    utcnow = datetime.fromisoformat(datetime_iso9601)
    date = utcnow.isoformat().split('.')[0]
    timestamp = int(utcnow.timestamp())

    d = {
      'host_uuid':host_uuid,
      'temperature': temperature,
      'timestamp': timestamp
    }
    self.colt.insert_one(d)

  def job(self):
    hosts = self.get_hosts()
    host_temps = []
    utcnow = datetime.utcnow()
    date = utcnow.isoformat().split('.')[0]
    timestamp = int(utcnow.timestamp())
    for host in hosts:
      host_uuid = host['uuid']
      host_ip = host['ip']

      try:
        command = f'snmpget -v 2c -c public {host_ip} 1.3.6.1.4.1.318.1.1.26.10.2.2.1.8.1'
        response = subprocess.check_output(command).decode()
        #response = 'SNMPv2-SMI::enterprises.318.1.1.26.10.2.2.1.8.1 = INTEGER: 329'
        words = response.split('INTEGER:')
        if len(words) != 2:
          continue
        temperature = int(words[1])/10
        host_temps.append({
          'host_uuid':host_uuid,
          'temperature': temperature,
          'timestamp': timestamp
        })
      except Exception as e:
        print(e, flush=True)

    print(host_temps, flush=True)

    if len(host_temps) != 0:
      self.colt.insert_many(host_temps)


def get_json(mongo_data):
  if mongo_data is None:
    raise fastapi.HTTPException(status_code=404, detail='Resource Not Found')
  return json.loads(bson.json_util.dumps(mongo_data))
