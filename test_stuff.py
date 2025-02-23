import read_sensor
import time
from MPU6050 import MPU6050

# Pass your MPU6050 Address
mpu = MPU6050.MPU6050(0x68)

# Init Settings
mpu.reset()
mpu.power_manage()
mpu.gyro_config()
mpu.accel_config()

bme280 = read_sensor.init_sensor()

while True:
   # Temperature Readings in Celsius
  print(f"mpu6050 Temperature values are {mpu.get_temperature()}")
  
  read_sensor.read_data(bme280, write_to_db=False)

  time.sleep(5)
