import time
import datetime
from smbus2 import SMBus
import sys
import logging

from bme280 import BME280
from send_email import send_email


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


recorded_temps = []

def div_0(num, den): ### returns 0 if den is 0
        return 0 if den == 0 else num / den

def read_data():
    _temperature = bme280.get_temperature()
    _pressure = bme280.get_pressure()
    _humidity = bme280.get_humidity()
    print(f"{_temperature:05.2f}°C {_pressure:05.2f}hPa {_humidity:05.2f}%")
    logging.info(f"{_temperature}°C {_pressure}hPa {_humidity}% {str(datetime.datetime.today())}")
    return _temperature, _pressure, _humidity


### DO THS FIRST TO FIRE UP THE SENSOR AND DISCARD THE FIRST VALUE
_temperature = bme280.get_temperature()
time.sleep(3)

### to keep track of number of iterations
i=1
while True:

    try:
        ### try read from the sensor, display an error message if there is an error
        try:
            temperature, pressure, humidity = read_data()
        except Exception as e:
            send_email(repr.e)
            raise e
    
        time.sleep(10)
    except Exception as e:
        send_email(e)
        raise e
