from pymongo import MongoClient
import bson.json_util
import json

def get_json(mongo_data):
  if mongo_data is None:
    raise Exception('fail')
  return json.loads(bson.json_util.dumps(mongo_data))

host = '127.0.0.1'
port = 27017
username = 'root'
password = 'example'

client = MongoClient(f'mongodb://{host}:{port}/',
  username=username, password=password)

colt = client['api_temperature']['temperature_v1']

result = colt.find_one({'host':'a'}, {'_id': False}, sort=[("timestamp", -1)])

if result is None:
  exit()

showing_range = 'day'
max_timestamp = result['timestamp']
if showing_range == 'month':
  min_timestamp = max_timestamp - 60 * 60 * 24 * 31
elif showing_range == 'week':
  min_timestamp = max_timestamp - 60 * 60 * 24 * 7
else:
  min_timestamp = max_timestamp - 60 * 60 * 24

print(max_timestamp)
print(min_timestamp)

result = colt.find({'host':'a', 'timestamp':{"$gt": min_timestamp}},
 {'_id': False}).sort([('timestamp', 1)])

j = get_json(result)
print(len(j))
