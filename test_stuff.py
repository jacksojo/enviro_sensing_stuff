import read_sensor
import time
from mpu6050 import mpu6050

# Pass your MPU6050 Address
mpu = mpu6050(0x68)

bme280 = read_sensor.init_sensor()

while True:
   # Temperature Readings in Celsius
  print(sensor.get_accel_data())
  
  read_sensor.read_data(bme280, write_to_db=False)

  time.sleep(5)
