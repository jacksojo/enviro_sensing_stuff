#!/usr/bin/env python

import time
import datetime
from smbus2 import SMBus
import sys
from PIL import Image, ImageDraw, ImageFont
import statistics
import requests
import logging

from bme280 import BME280
import st7789

# check if calibration Q value is passed
#try:
#  QNH_VALUE = int(sys.argv[1])
#except:
#  QNH_VALUE = 1010
#  print('using default QNH value. go to https://metar-taf.com/CAE2 to find a real value')
#print(f'Running with QNH of {QNH_VALUE}')

# setup logging
logging.basicConfig(filename='temps_'+str(datetime.date.today())+'.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


# Initialise the BME280
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)


# Initialise the st7789

disp = st7789.ST7789(
        height=240,
        rotation=90,
        port=0,
        cs=st7789.BG_SPI_CS_FRONT, 
        dc=9,
        backlight=19,  
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0,
    )


disp.begin()

WIDTH = disp.width
HEIGHT = disp.height

img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)

recorded_temps = []

def div_0(num, den): ### returns 0 if den is 0
        return 0 if den == 0 else num / den

def get_metar(icao_id='CYXC'):
    raw = requests.get('https://aviationweather.gov/api/data/metar?ids={icao_id}', headers={'accept': 'json'})
    print(raw)
    components = raw.json['rawOb'].split(' ')
    for c in components:
        if c[0] == 'A':
          a_value = c[1:]
    q_value = a_value * 33.863886666667
    return q_value

def read_data():
    _altitude = bme280.get_altitude(qnh=QNH)
    _temperature = bme280.get_temperature()
    _pressure = bme280.get_pressure()
    _humidity = bme280.get_humidity()
    print(f"{_temperature:05.2f}°C {_pressure:05.2f}hPa {_humidity:05.2f}% {_altitude:05.2f}m")
    logging.info(f"{_temperature}°C {_pressure}hPa {_humidity}% {_altitude}m {str(datetime.datetime.today())}")
    return _temperature, _pressure, _humidity, _altitude

def terminate(error_text=' '):
    disp.reset()
    draw.text((5, 5), error_text, font=font, fill=(255,255,255))
    disp.display(img)
    time.sleep(3)
    disp.display(Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0)))
    disp.set_backlight(0)
    sys.exit()

def set_background_colour(temp):
    avg_temp = statistics.mean(recorded_temps)
    try:
        std_dev = statistics.stdev(recorded_temps)
    except:
        std_dev = 1

    std_devs_from_mean = div_0(temp - avg_temp, std_dev)
    std_devs_from_mean = std_devs_from_mean * -1 if std_devs_from_mean < 0 else std_devs_from_mean
    amplitude = int(255 * std_devs_from_mean / 3)
    amplitude = 255 if amplitude > 255 else amplitude

    if temp > avg_temp: # closer to max = more red
        return (amplitude, 20, 0)
    elif temperature < avg_temp: # closer to min = more blue
        return (0, 20, amplitude)
    else:
        return (0, 20, 0)
      
### DO THS FIRST TO FIRE UP THE SENSOR AND DISCARD THE FIRST VALUE      
QNH = get_metar()
print('using QNH', QNH)
_altitude = bme280.get_altitude(qnh=QNH)
time.sleep(1)

### to keep track of number of iterations
i=1
while True:
    if i % 10 == 0:
        QNH = get_metar()
        print('using QNH', QNH)
    i += 1

    try:
        ### try read from the sensor, display an error message if there is an error
        try:
            temperature, pressure, humidity, altitude = read_data(QNH)
            recorded_temps.append(temperature)
        except:
            raise
            terminate('BME280 \n ERROR')
    
        ### update the background colour based on the current temp relative to the last 2 mins
        if len(recorded_temps) > 120:
            recorded_temps = recorded_temps[-120:]
    
        background_colour = set_background_colour(temperature)
    
        draw.rectangle((0, 0, WIDTH, HEIGHT), background_colour)
    
        ### add in the temperature text
        draw.text((5, 5), f"{temperature:05.2f}°C", font=font, fill=(255, 255, 255))
        draw.text((5, 85), f"{pressure:05.2f}hPa", font=font, fill=(255, 255, 255))
        draw.text((5, 165), f"{humidity:05.2f}%", font=font, fill=(255, 255, 255))
        disp.display(img)
    
        time.sleep(10)
    except KeyboardInterrupt:
        terminate('keyboard \ninterrupt')
    except Exception as e:
        terminate(e)
