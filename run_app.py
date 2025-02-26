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

# Shared queue for display requests
display_queue = queue.Queue()
display_active = Event()

@dataclass
class DisplayRequest:
    show_on_screen: bool = False

def handle_display_error(display, error):
    error_message = f"Display error: {repr(error)}"
    print(error_message)
    logging.error(error_message, exc_info=True)
    send_email(error_message)
    display.set_backlight(False)
    display_active.clear()

def generate_and_save_image(display):
    print("Generating new image...")
    image = display_data.build_image(display)
    display_data.save_image(image)
    return image

def show_on_physical_display(display, image):
    print("Showing image on display")
    display.set_backlight(True)
    display_data.display_image_on_screen(display, image)
    print("Image displayed successfully")
    display_active.set()
    time.sleep(DISPLAY_TIMEOUT)
    display.set_backlight(False)
    print('Display turned off')
    display_active.clear()

def display_loop(display):
    while True:
        try:
            request = display_queue.get()
            print("Display request received")
            
            image = generate_and_save_image(display)
            
            if request.show_on_screen:
                show_on_physical_display(display, image)
                
        except Exception as e:
            handle_display_error(display, e)

def sensor_loop(sensor, error_count=0):
    while True:
        try:
            temperature, humidity, pressure = read_sensor.read_data(sensor)
            print(f"Sensor reading: {temperature}°C {pressure}hPa {humidity}%")
            time.sleep(TIME_BETWEEN_READINGS)
            continue
        except Exception as e:
            error_message = f"Sensor reading error: {repr(e)}"
            print(error_message)
            logging.error(error_message, exc_info=True)
            send_email(error_message)
            
        error_count += 1
        if error_count >= 3:
            error_message = 'Process terminated due to repeated errors.'
            print(error_message)
            send_email(error_message)
            logging.error(error_message)
            sys.exit()
            
        time.sleep(TIME_BETWEEN_READINGS)

def motion_loop(motion_line):
    while True:
        if motion_sensor.check_motion(motion_line) and not display_active.is_set():
            print('Motion detected - Triggering display update')
            display_queue.put(DisplayRequest(show_on_screen=True))
        time.sleep(0.1)

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
    run_web_server.run(display_queue)

if __name__ == "__main__":
    main()
