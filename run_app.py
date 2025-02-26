import time
import logging
import read_sensor
import display_data
import run_web_server
import motion_sensor
from send_email import send_email
import sys
from pathlib import Path
from threading import Thread, Event
import queue

SCRIPT_DIR = Path(__file__).parent
TIME_BETWEEN_READINGS = 60
LOG_FILE = SCRIPT_DIR / 'logs' / "error_log.log"
DISPLAY_TIMEOUT = 10  # seconds

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Shared queue for display requests
display_queue = queue.Queue()
display_active = Event()

def sensor_loop(sensor, error_count=0):
    while True:
        if error_count == 3:
            send_email('Process terminated due to repeated errors.')
            logging.error("Process terminated after 3 consecutive errors.")
            sys.exit()

        try:
            read_sensor.read_data(sensor)
            error_count = 0
        except Exception as e:
            error_message = f"Sensor reading error: {repr(e)}"
            print(error_message)
            logging.error(error_message, exc_info=True)
            send_email(error_message)
            error_count += 1

        time.sleep(TIME_BETWEEN_READINGS)

def display_loop(display):
    while True:
        try:
            # Wait for display request
            display_queue.get()
            
            # Generate and show image
            image = display_data.build_image(display)
            display_data.save_image(image)
            display_data.display_image_on_screen(display, image)
            
            # Set display active
            display_active.set()
            
            # Wait for timeout
            time.sleep(DISPLAY_TIMEOUT)
            
            # Turn off display
            display.set_backlight(False)
            display_active.clear()
            
        except Exception as e:
            error_message = f"Display error: {repr(e)}"
            print(error_message)
            logging.error(error_message, exc_info=True)
            send_email(error_message)

def motion_loop(motion_line):
    while True:
        if motion_sensor.check_motion(motion_line):
            if not display_active.is_set():
                display_queue.put(True)
        time.sleep(0.1)  # Small delay to prevent CPU overuse

def main():
    # Initialize components
    sensor = read_sensor.init_sensor()
    display = display_data.init_display()
    motion_line = motion_sensor.init_motion_sensor()
    
    # Take initial reading
    read_sensor.take_throwaway_reading(sensor)
    
    # Start threads
    Thread(target=sensor_loop, args=(sensor,), daemon=True).start()
    Thread(target=display_loop, args=(display,), daemon=True).start()
    Thread(target=motion_loop, args=(motion_line,), daemon=True).start()
    
    # Start web server (main thread)
    run_web_server.run(display_queue)

if __name__ == "__main__":
    main()
