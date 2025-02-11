import time
import read_sensor
import display_data
import run_web_server
from send_email import send_email
import sys

TIME_BETWEEN_READINGS = 60

## initialise stuff
sensor = read_sensor.init_sensor()
display = display_data.init_display()

## take a reading and discard
read_sensor.take_throwaway_reading(sensor)

## run the loop
error_count = 0
while True:

    if error_count == 3:
        send_email('process_terminated')
        ### need to add something about shutting down screen here
        sys.exit()

    try:
        read_sensor.read_data(sensor)
    except Exception as e:
        print(e)
        send_email(repr(e))
        error_count += 1
        pass
    
    time.sleep(2)

    try:
        image = display_data.build_image(display)
        display_data.save_image(image)
        display_data.display_image_on_screen(display, image)
    except Exception as e:
        print(e)
        send_email(repr(e))
        error_count += 1
        pass

    error_count = 0

    time.sleep(TIME_BETWEEN_READINGS-2)
