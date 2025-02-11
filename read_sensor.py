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
    logging.basicConfig(filename='/home/jonathan/Code/environment_sensing/enviro_sensing_stuff/logs/temps_'+str(datetime.date.today())+'.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

setup_logging()

# Initialise the BME280
def init_sensor():
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)
    return bme280

def take_throwaway_reading(bme280):
    return bme280.get_temperature


def read_data(bme280):

    timestamp = datetime.datetime.now()
    db_table = db_utils.BME280_TABLE_DEF

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()

    logging.info(f"{temperature}°C {pressure}hPa {humidity}%")
    print(f"{temperature}°C {pressure}hPa {humidity}%")

    payload = {
            'timestamp':f"'{str(timestamp)}'",
            'temperature':temperature, 
            'humidity':humidity, 
            'pressure':pressure
        }

    db_utils.write_row_to_db(db_table['table_name'], payload)

    return temperature, humidity, pressure
