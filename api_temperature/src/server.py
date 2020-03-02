import os
import mongo
from fastapi import FastAPI, HTTPException

host = os.environ['MONGO_HOST']
port = int(os.environ['MONGO_PORT'])
username = os.environ['MONGO_USER']
password = os.environ['MONGO_PASS']
TClient = mongo.TemperatureClient(host, port, username, password)
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
async def get_temperatures(host_name:str):
  return TClient.get_host_temperatures(host_name)
