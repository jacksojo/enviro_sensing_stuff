import requests
import os
import send_email
import json

postcode = 'V1A2Y9'
api_key = os.environ['FREE_WEATHER_API_KEY']
url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={postcode}&aqi=yes'

raw = requests.get(url, headers={'connection': 'close'})

raw_json = json.loads(raw.body)

try:
  print(raw)
except Exception as e:
  raise e
