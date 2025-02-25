import time
import logging
import read_sensor
import display_data
import run_web_server
from send_email import send_email
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent


TIME_BETWEEN_READINGS = 60
LOG_FILE = SCRIPT_DIR / 'logs' / "error_log.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialise stuff
sensor = read_sensor.init_sensor()
display = display_data.init_display()

# Take a reading and discard
read_sensor.take_throwaway_reading(sensor)

# Run the loop
error_count = 0
while True:
    if error_count == 3:
        send_email('Process terminated due to repeated errors.')
        logging.error("Process terminated after 3 consecutive errors.")
        ### Add logic to shut down the display here if needed
        sys.exit()

    try:
        read_sensor.read_data(sensor)
    except Exception as e:
        error_message = f"Sensor reading error: {repr(e)}"
        print(error_message)
        logging.error(error_message, exc_info=True)
        send_email(error_message)
        error_count += 1
        continue
    
    time.sleep(2)

    try:
        image = display_data.build_image(display)
        display_data.save_image(image)
        display_data.display_image_on_screen(display, image)
    except Exception as e:
        error_message = f"Display error: {repr(e)}"
        print(error_message)
        logging.error(error_message, exc_info=True)
        send_email(error_message)
        error_count += 1
        continue

    error_count = 0  # Reset error count after a successful iteration
    time.sleep(TIME_BETWEEN_READINGS - 2)
