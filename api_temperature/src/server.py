import os
import client
import fastapi
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

host = os.environ['MONGO_HOST']
port = int(os.environ['MONGO_PORT'])
username = os.environ['MONGO_USER']
password = os.environ['MONGO_PASS']
erase_db = os.environ['ERASE_DB'].lower() == 'true'
auto_collect = os.environ['AUTO_COLLECT'].lower() == 'true'
TClient = client.TemperatureClient(host, port, username, password,
                                  erase_db, auto_collect)
app = FastAPI()

#############
## summary ##
#############

@app.get("/api/temperature/v1/summary/")
async def get_hosts():
  return TClient.get_summary()

###########
## hosts ##
###########

@app.get("/api/temperature/v1/hosts/")
async def get_hosts():
  return TClient.get_hosts()

@app.put("/api/temperature/v1/hosts/")
async def put_hosts(request:Request):
  try:
    j = await request.json()
    name = j['name']
    ip = j['ip']
  except Exception as e:
    print(e)
    raise fastapi.HTTPException(status_code=400, detail='Json Decode Error')
  TClient.add_host(name, ip)
  return TClient.get_hosts()

@app.delete("/api/temperature/v1/hosts/{host_uuid}")
async def delete_hosts(host_uuid:str):
  TClient.rm_host(host_uuid)
  return TClient.get_hosts()

##################
## temperatures ##
##################

@app.get("/api/temperature/v1/temperatures/{host_uuid}")
async def get_temperatures(host_uuid:str, showing_range:str='day'):
  return TClient.get_host_temperatures(host_uuid, showing_range)

@app.put("/api/temperature/v1/temperatures/")
async def put_temperatures(request:Request):
  try:
    j = await request.json()
    host_uuid = j['host_uuid']
    datetime_iso9601 = j['datetime']
    temperature = j['temperature']
  except Exception as e:
    print(e)
    raise fastapi.HTTPException(status_code=400, detail='Json Decode Error')
  TClient.add_host_temperature(host_uuid, datetime_iso9601, temperature)
  return {}

#######################
## all for delete db ##
#######################

@app.delete("/api/temperature/v1/all/")
async def delete_all():
  TClient.rm_all()
  return {}
  