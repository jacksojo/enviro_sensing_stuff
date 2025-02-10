import time
import datetime
from smbus2 import SMBus
import sys
import logging
import sqlite3

from bme280 import BME280
from send_email import send_email
import db_utils


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
    return _temperature, _pressure, _humidity


### DO THS FIRST TO FIRE UP THE SENSOR AND DISCARD THE FIRST VALUE
_temperature = bme280.get_temperature()
time.sleep(3)


while True:
    timestamp = datetime.datetime.now()
    db_table = db_utils.BME280_TABLE_DEF
    try:
        temperature, humidity, pressure = read_data()
        payload = {
            'id':int(timestamp.timestamp()), 
            'timestamp':str(timestamp), 
            'temperature':temperature, 
            'humidity':humidity, 
            'pressure':pressure
        }
        
        print(f"{temperature:05.2f}°C {pressure:05.2f}hPa {humidity:05.2f}%") 
        db_utils.write_row_to_db(db_table['table_name'], payload)

        time.sleep(10)
        
    except Exception as e:
        send_email(rep(e))
        raise e

