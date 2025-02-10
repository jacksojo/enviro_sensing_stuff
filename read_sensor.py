import time
import datetime
from smbus2 import SMBus
import sys
import logging
import sqlite3

from bme280 import BME280
from send_email import send_email
import db_utils

TIME_BETWEEN_READINGS = 60


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


def read_data():
    _temperature = bme280.get_temperature()
    _pressure = bme280.get_pressure()
    _humidity = bme280.get_humidity()
    logging.info(f"{_temperature}°C {_pressure}hPa {_humidity}%m")
    return _temperature, _humidity, _pressure


### DO THS FIRST TO FIRE UP THE SENSOR AND DISCARD THE FIRST VALUE
_temperature = bme280.get_temperature()
time.sleep(3)

while True:
    timestamp = datetime.datetime.now()
    db_table = db_utils.BME280_TABLE_DEF
    try:
        temperature, humidity, pressure = read_data()
        payload = {
            'timestamp':f"'{str(timestamp)}'",
            'temperature':temperature, 
            'humidity':humidity, 
            'pressure':pressure
        }
        
        print(f"{temperature:05.2f}°C {pressure:05.2f}hPa {humidity:05.2f}%") 
        db_utils.write_row_to_db(db_table['table_name'], payload)

        time.sleep(TIME_BETWEEN_READINGS)
        
    except Exception as e:
        send_email(repr(e))
        raise e

