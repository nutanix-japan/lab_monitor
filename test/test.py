import requests
import json

def main():
  add_hosts()
  add_temperatures()

def add_hosts():
  hosts = [
    {
      'name':'a',
      'ip':'10.0.0.101'
    },
    { 
      'name':'b', 
      'ip':'10.0.0.102'
    }
  ]
  for host in hosts:
    requests.put('http://127.0.0.1/api/temperature/v1/hosts/', data=json.dumps(host))

def add_temperatures():
  result = requests.get('http://127.0.0.1/api/temperature/v1/hosts/')
  host = result.json()[0]
  host_uuid = host['uuid']

  '''
  for m in range(7, 9):
    for d in range(1, 32):
      for h in range(24):
        for mi in range(60):
          add2(host_uuid, m, d, h, mi)
  '''

  for h in range(24):
    for mi in range(60):
      add2(host_uuid, 3, 5, h, mi)

def add2(host_uuid, m, d, h, mi):
  month = str(m).zfill(2)
  day = str(d).zfill(2)
  hour = str(h).zfill(2)
  minute = str(mi).zfill(2)
  t = f'2020-{month}-{day}T{hour}:{minute}:00'
  u = f'http://127.0.0.1/api/temperature/v1/temperatures/'
  d = {
    'host_uuid': host_uuid,
    'datetime': t,
    'temperature': h % 10 + 20
  }
  requests.put(u, data=json.dumps(d))

if __name__ == '__main__':
  main()