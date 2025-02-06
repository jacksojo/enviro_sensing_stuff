#!/usr/bin/env python

import time
import datetime
from smbus2 import SMBus
import sys
from PIL import Image, ImageDraw, ImageFont
import statistics
import requests
import logging
import os
from send_email import send_email
from get_local_weather import get_local_weather


from bme280 import BME280
import st7789

# setup logging
def setup_logging():
    logging.basicConfig(filename='logs/temps_'+str(datetime.date.today())+'.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

setup_logging()

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
small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

recorded_temps = []

def div_0(num, den): ### returns 0 if den is 0
        return 0 if den == 0 else num / den

def read_data():
    _altitude = '000'
    _temperature = bme280.get_temperature()
    _pressure = bme280.get_pressure()
    _humidity = bme280.get_humidity()
    _temp_from_api = current_weather['current']['temp_c']
    print(f"{_temperature:05.2f}°C {_pressure:05.2f}hPa {_humidity:05.2f}%")
    logging.info(f"{_temperature}°C {_pressure}hPa {_humidity}% {_altitude}m {str(datetime.datetime.today())} local_temp:{_temp_from_api}°C")
    return _temperature, _pressure, _humidity, _temp_from_api

# I don't think this works properly
def terminate(error_text=' '):
    disp.reset()
    draw.text((5, 5), repr(error_text), font=font, fill=(255,255,255))
    disp.display(img)
    time.sleep(3)
    disp.display(Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0)))
    disp.set_backlight(0)
    sys.exit()

### this will change the background colour of the display to match the temperature trend
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
_temperature = bme280.get_temperature()

current_weather = get_local_weather()

### to keep track of number of iterations
i=1
while True:
    setup_logging()

    try:
        current_weather = get_local_weather()
    except:
        pass

    try:
        ### try read from the sensor, display an error message if there is an error
        try:
            temperature, pressure, humidity, temp_from_api = read_data()
            recorded_temps.append(temperature)
        except Exception as e:
            send_email(e)
            raise
            terminate('BME280 \n ERROR')
    
        ### update the background colour based on the current temp relative to the last 2 mins
        if len(recorded_temps) > 120:
            recorded_temps = recorded_temps[-120:]
    
        background_colour = set_background_colour(temperature)
    
        draw.rectangle((0, 0, WIDTH, HEIGHT), background_colour)
    
        ### add in the temperature text
        draw.text((5, 15), f"{temperature:05.2f}°C", font=font, fill=(255, 255, 255))
        draw.text((5, 55), f"{temp_from_api:05.2f}°C in town", font=small_font, fill=(255, 255, 255))
        draw.text((5, 95), f"{pressure:05.2f}hPa", font=font, fill=(255, 255, 255))
        draw.text((5, 155), f"{humidity:05.2f}%", font=font, fill=(255, 255, 255))
        draw.text((5, 215), f"{str(time.ctime())}", font=small_font, fill=(255, 255, 255))
        disp.display(img)
    
        time.sleep(60)
    except Exception as e:
        send_email(e)
        terminate(e)
