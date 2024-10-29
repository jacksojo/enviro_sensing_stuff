#!/usr/bin/env python

import time
from smbus2 import SMBus
import sys
from PIL import Image, ImageDraw, ImageFont
import statistics

from bme280 import BME280
import st7789


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

while True:

    ### try read from the sensor, display an error message if there is an error
    try:
        temperature = bme280.get_temperature()
        recorded_temps.append(temperature)
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
        print(f"{temperature:05.2f}°C {pressure:05.2f}hPa {humidity:05.2f}%")
    except:
        print('error reading data from bme280')
        draw.text((5, 5), "BME280 \nERROR", font=font, fill=(255,255,255))
        disp.display(img)
        time.sleep(3)
        disp.reset() ### not sure this does anything?
        disp.display(Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0)))
        sys.exit()

    ### update the background colour based on the current temp relative to the last 2 mins
    if len(recorded_temps) > 120:
        recorded_temps = recorded_temps[-120:]

    def div_0(num, den): ### returns 0 if den is 0
        return 0 if den == 0 else num / den

    avg_temp = statistics.mean(recorded_temps)
    std_dev = statistics.stddev(recorded_temps)

    std_devs_from_mean = temperature - div_0(avg_temp, std_dev)
    std_devs_from_mean = std_devs_from_mean * -1 if std_devs_from_mean < 0
    amplitude = int(255 / std_devs_from_mean / 3)
    amplitude = 255 if amplitude > 255

    if temperature > avg_temp: # closer to max = more red
        colour = (amplitude, 0, 0)
    elif temperature < avg_temp: # closer to min = more blue
        colour = (0, 0, amplitude)
    else:
        colour = (0, 0, 0)

    draw.rectangle((0, 0, WIDTH, HEIGHT), tuple(colour))
    draw.text((5, 5), f"{temperature:05.2f}°C", font=font, fill=(255, 255, 255))
    draw.text((5, 85), f"{pressure:05.2f}hPa", font=font, fill=(255, 255, 255))
    draw.text((5, 165), f"{humidity:05.2f}%", font=font, fill=(255, 255, 255))
    disp.display(img)

    time.sleep(1)
