import time
import schedule
import subprocess
import threading
from datetime import datetime
from pymongo import MongoClient

import bson.json_util
import fastapi
import json

class TemperatureClient:

  DB_TEMPERATURE = 'api_temperature'
  COL_HOST = 'host_v1'
  COL_TEMPERATURE = 'temperature_v1'

  def __init__(self, host, port, username, password, erase_db=False):
    client = MongoClient(f'mongodb://{host}:{port}/',
      username=username, password=password)

    if erase_db:
      client.drop_database(DB_TEMPERATURE)
    self.colh = client[self.DB_TEMPERATURE][self.COL_HOST]
    self.colt = client[self.DB_TEMPERATURE][self.COL_TEMPERATURE]

    def fun():
      schedule.every().minutes.do(self.job)
      while True:
        schedule.run_pending()
        time.sleep(1)
    threading.Thread(target=fun).start()

  def get_hosts(self):
    hosts = []
    for host in self.colh.find():
      hosts.append(host['host'])
    return hosts

  def add_host(self, host):
    host = host.strip()
    if self.colh.find({'host':host}).count() >= 1:
      return
    d = {
      'host':host
    }
    self.colh.insert_one(d)

  def rm_host(self, host):
    host = host.strip()
    self.colh.delete_many({'host':host})
    self.colt.delete_many({'host':host})

  def get_host_temperatures(self, host, limit=60*24):
    result = self.colt.find({'host':host}, {'_id': False}).sort(
      [('timestamp', 1)]).limit(limit)
    return get_json(result)

  def job(self):
    hosts = self.get_hosts()
    host_temps = []
    timestamp = int(datetime.utcnow().timestamp())
    for host in hosts:
      try:
        '''
        command = f'snmpget -v 2c -c public {host} 1.3.6.1.4.1.318.1.1.26.10.2.2.1.8.1'
        response = subprocess.check_output(command).decode()
        '''
        response = 'SNMPv2-SMI::enterprises.318.1.1.26.10.2.2.1.8.1 = INTEGER: 329'
        words = response.split('INTEGER:')
        if len(words) != 2:
          continue
        temperature = int(words[1])/10
        host_temps.append({
          'host':host,
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
