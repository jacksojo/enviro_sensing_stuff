import read_sensor
import time

bme280 = read_sensor.init_sensor()

while True:
  read_sensor.read_data(bme280, write_to_db=False)

  time.sleep(5)
