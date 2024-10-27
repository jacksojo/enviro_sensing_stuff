#!/usr/bin/env python

import time
from smbus2 import SMBus
import sys
from PIL import Image, ImageDraw, ImageFont

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

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)

size_x, size_y = draw.textsize("HI", font)

text_x = disp.width
text_y = (disp.height - size_y) // 2

while True:
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()

    draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))
    draw.text((5, 5), f"{temperature:05.2f}°C", font=font, fill=(255, 255, 255))
    draw.text((5, 55), f"{pressure:05.2f}hPa", font=font, fill=(255, 255, 255))
    draw.text((5, 105), f" {humidity:05.2f}%", font=font, fill=(255, 255, 255))

    time.sleep(1)
