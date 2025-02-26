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
from dataclasses import dataclass

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

# Global state variables
GENERATE_IMAGE = False
DISPLAY_IMAGE_ON_SCREEN = False

def set_display_flags(gen_image=None, show_on_screen=None):
    global GENERATE_IMAGE, DISPLAY_IMAGE_ON_SCREEN
    if gen_image is not None:
        GENERATE_IMAGE = gen_image
    if show_on_screen is not None:
        DISPLAY_IMAGE_ON_SCREEN = show_on_screen

def clear_display():
    display.set_backlight(False)
    display_active.clear()
    print('display turned off')

def handle_error(error):
    error_message = f"error: {repr(error)}"
    print(error_message)
    logging.error(error_message, exc_info=True)
    send_email(error_message)
    clear_display()

def generate_image(display):
    print("Generating new image...")
    image = display_data.build_image(display)
    display_data.save_image(image)
    return image

def show_on_physical_display(display, image):
    print("Showing image on screen")
    display.set_backlight(True)
    display_data.display_image_on_screen(display, image)
    print("Image displayed successfully")
    display_active.set()
    time.sleep(DISPLAY_TIMEOUT)
    clear_display()

def display_loop(display):
    while True:
        if GENERATE_IMAGE:
            image = generate_image(display)
            set_display_flags(gen_image=FALSE)
            
            if DISPLAY_IMAGE_ON_SCREEN:
                show_on_physical_display(display, image)
                set_display_flags(show_on_screen=FALSE)
        time.sleep(0.1)

def sensor_loop(sensor, error_count=0):
    while True:
        try:
            temperature, humidity, pressure = read_sensor.read_data(sensor)
            print(f"Sensor reading: {temperature}°C {pressure}hPa {humidity}%")
            time.sleep(TIME_BETWEEN_READINGS)
            continue
        except Exception as e:
            handle_error(e)
            error_count += 1

        if error_count >= 3:
            handle_error('Process terminated due to repeated errors.')
            sys.exit()
            
        time.sleep(TIME_BETWEEN_READINGS)

def motion_loop(motion_line):
    while True:
        if motion_sensor.check_motion(motion_line) and not GENERATE_IMAGE:
            print('Motion detected - Triggering display update')
            set_display_flags(gen_image=True, show_on_screen=True)
            time.sleep(DISPLAY_TIMEOUT-2)
        time.sleep(1)

def main():
    print("Initializing components...")
    sensor = read_sensor.init_sensor()
    display = display_data.init_display()
    motion_line = motion_sensor.init_motion_sensor()
    print("Components initialized successfully")
    
    print("Taking initial sensor reading...")
    read_sensor.take_throwaway_reading(sensor)
    
    Thread(target=sensor_loop, args=(sensor,), daemon=True).start()
    Thread(target=display_loop, args=(display,), daemon=True).start()
    Thread(target=motion_loop, args=(motion_line,), daemon=True).start()
    
    print("Starting web server...")
    run_web_server.run()

if __name__ == "__main__":
    main()
