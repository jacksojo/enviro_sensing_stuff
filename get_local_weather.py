import requests
import os
from send_email import send_email

postcode = 'V1A2Y9'
api_key = os.environ['FREE_WEATHER_API_KEY']
url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={postcode}&aqi=yes'

def get_local_weather():

    raw = requests.get(url, headers={'connection': 'close'})   
    raw_json = raw.json()
    
    try:
        return raw_json
    except Exception as e:
        send_email(e)
        raise e
