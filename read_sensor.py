import time
import datetime
from smbus2 import SMBus
from bme280 import BME280
import db_utils

TIME_BETWEEN_READINGS = 60

# Initialise the BME280
def init_sensor():
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)
    return bme280


def read_data(bme280, write_to_db=True):
    timestamp = datetime.datetime.now()
    db_table = db_utils.BME280_TABLE_DEF

    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()

    payload = {
            'timestamp':f"'{str(timestamp)}'",
            'temperature':temperature, 
            'humidity':humidity, 
            'pressure':pressure
        }

    if write_to_db:
        db_utils.write_row_to_db(db_table['table_name'], payload)

    return temperature, humidity, pressure
