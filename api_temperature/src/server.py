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

@app.get("/api/temperature/v1/hosts/")
async def get_hosts():
  return TClient.get_hosts()

@app.put("/api/temperature/v1/hosts/{host_name}")
async def put_hosts(host_name:str):
  TClient.add_host(host_name)
  return TClient.get_hosts()

@app.delete("/api/temperature/v1/hosts/{host_name}")
async def delete_hosts(host_name:str):
  TClient.rm_host(host_name)
  return TClient.get_hosts()

@app.get("/api/temperature/v1/temperatures/{host_name}")
async def get_temperatures(host_name:str, showing_range:str='day'):
  return TClient.get_host_temperatures(host_name, showing_range)

@app.put("/api/temperature/v1/temperatures/{host_name}")
async def put_temperatures(request:Request, host_name:str):
  try:
    j = await request.json()
    host = host_name
    datetime_iso9601 = j['datetime']
    temperature = j['temperature']
  except Exception as e:
    print(e)
    raise fastapi.HTTPException(status_code=400, detail='Json Decode Error')
  TClient.add_host_temperature(host_name, datetime_iso9601, temperature)
  return {}