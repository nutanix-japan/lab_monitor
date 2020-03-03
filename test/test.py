import requests
import json

def main():
  add_hosts()
  add_temperatures()

def add_hosts():
  hosts = ['a', 'b', 'c', 'd']
  for host in hosts:
    u = f'http://127.0.0.1/api/temperature/v1/hosts/{host}'
    requests.put(u)

def add_temperatures():
  for m in range(7, 9):
    for d in range(1, 32):
      for h in range(24):
        for mi in range(60):
          add2(m, d, h, mi)
      print(m, d)

def add2(m, d, h, mi):
  month = str(m).zfill(2)
  day = str(d).zfill(2)
  hour = str(h).zfill(2)
  minute = str(mi).zfill(2)
  t = f'2020-{month}-{day}T{hour}:{minute}:00'
  u = f'http://127.0.0.1/api/temperature/v1/temperatures/{"a"}'
  d = {
    'host':'a',
    'datetime': t,
    'temperature': h % 10 + 20
  }
  requests.put(u, data=json.dumps(d))

if __name__ == '__main__':
  main()