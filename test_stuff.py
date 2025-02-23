import read_sensor
import time
from mpu6050 import mpu6050
import smbus

bus = smbus.SMBus(0)

# Pass your MPU6050 Address
mpu = mpu6050(0x68, bus=0)

bme280 = read_sensor.init_sensor()

while True:

  print(mpu.get_gyro_data)

  time.sleep(1)
