import motion_sensor
import time

motion_line = motion_sensor.init_motion_sensor()

while True:
  reading = motion_sensor.check_motion(motion_line)
  print('motion: ', reading)
  time.sleep(1)
