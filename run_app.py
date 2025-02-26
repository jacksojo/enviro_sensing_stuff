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
            error_message = 'Process terminated due to repeated errors.'
            print(error_message)
            send_email(error_message)
            logging.error(error_message)
            sys.exit()

        try:
            temperature, humidity, pressure = read_sensor.read_data(sensor)
            print(f"Sensor reading: {temperature}°C {pressure}hPa {humidity}%")
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
            print("Display request received")
            
            # Turn on display first
            display.set_backlight(True)
            print("Display backlight on")
            
            # Generate and show image
            try:
                print("Generating new image...")
                image = display_data.build_image(display)
                display_data.save_image(image)
                display_data.display_image_on_screen(display, image)
                print("Image displayed successfully")
            except Exception as e:
                error_message = f"Error generating/displaying image: {repr(e)}"
                print(error_message)
                logging.error(error_message, exc_info=True)
                display.set_backlight(False)
                display_active.clear()
                continue
            
            # Set display active
            display_active.set()
            
            # Wait for timeout
            time.sleep(DISPLAY_TIMEOUT)
            
            # Turn off display
            display.set_backlight(False)
            print('Display turned off')
            display_active.clear()
            
        except Exception as e:
            error_message = f"Display error: {repr(e)}"
            print(error_message)
            logging.error(error_message, exc_info=True)
            send_email(error_message)
            
            # Ensure display is off and status is cleared in case of error
            try:
                display.set_backlight(False)
                display_active.clear()
            except:
                pass

def motion_loop(motion_line):
    while True:
        if motion_sensor.check_motion(motion_line):
            print('Motion detected')
            if not display_active.is_set():
                print('Triggering display update')
                display_queue.put(True)
        time.sleep(0.1)  # Small delay to prevent CPU overuse

def main():
    print("Initializing components...")
    # Initialize components
    sensor = read_sensor.init_sensor()
    display = display_data.init_display()
    motion_line = motion_sensor.init_motion_sensor()
    print("Components initialized successfully")
    
    # Take initial reading
    print("Taking initial sensor reading...")
    read_sensor.take_throwaway_reading(sensor)
    
    # Start threads
    print("Starting sensor thread...")
    Thread(target=sensor_loop, args=(sensor,), daemon=True).start()
    print("Starting display thread...")
    Thread(target=display_loop, args=(display,), daemon=True).start()
    print("Starting motion detection thread...")
    Thread(target=motion_loop, args=(motion_line,), daemon=True).start()
    
    print("Starting web server...")
    # Start web server (main thread)
    run_web_server.run(display_queue)

if __name__ == "__main__":
    main()
