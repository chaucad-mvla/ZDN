from flask import render_template
from flask import Flask

from threading import Thread
import requests
import json
import time


def get_info():
  client = requests.Session()
  headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
  }
  request = client.get('https://www.nitromath.com/api/v2/teams/ZDN', headers=headers)
  
  data = []
  for member in request.json()['results']['members']:
    data.append({
        'username': member['username'],
        'max': member['highestSpeed'],
        'online': member['lastLogin'],
        'races': member['played'],
        'total': member['racesPlayed']
    })

  return data

def refresh(x):
  global rdata
  while True:
      rdata = get_info()
      time.sleep(x)

def daily_check():
  global ddata
  while True:
    for racer in get_info():
        ddata[racer['username']] = racer['races']
    time.sleep(86400)


app = Flask(__name__)

@app.route('/')
def index():
  global rdata, ddata

  data = []
  races = [racer['races'] for racer in rdata]
  races.sort()

  alrchecked = []
  for count in races:
    for mem in rdata:
      if mem['races'] == count and mem['username'] not in alrchecked:
        mem.update({'daily': mem['races']-ddata[mem['username']]})
        data.append(mem)
        alrchecked.append(mem['username'])
  data.reverse()

  return render_template('index.html', data=data)


rdata = []
ddata = {}
Thread(target=daily_check).start()
Thread(target=lambda: refresh(120)).start()
app.run(host='0.0.0.0', port=8080)
