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
from multiprocessing import Value
import ctypes

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
GENERATE_IMAGE = Value(ctypes.c_bool, False)
DISPLAY_IMAGE_ON_SCREEN = Value(ctypes.c_bool, False)   
DISPLAY = None  # Will be initialized in main()

def set_display_flags(gen_image=None, show_on_screen=None):
    if gen_image is not None:
        GENERATE_IMAGE.value = gen_image
    if show_on_screen is not None:
        DISPLAY_IMAGE_ON_SCREEN.value = show_on_screen

def clear_display():
    DISPLAY.set_backlight(False)
    print('display turned off')

def handle_error(error):
    error_message = f"error: {repr(error)}"
    print(error_message)
    logging.error(error_message, exc_info=True)
    send_email(error_message)
    clear_display()

def generate_image():
    print("Generating new image...")
    image = display_data.build_image(DISPLAY)
    display_data.save_image(image)
    print('new image saved')
    return image

def show_on_physical_display(image):
    print("Showing image on screen")
    DISPLAY.set_backlight(True)
    display_data.display_image_on_screen(DISPLAY, image)
    print("Image displayed successfully")
    time.sleep(DISPLAY_TIMEOUT)
    clear_display()

def display_loop():
    while True:
        if GENERATE_IMAGE.value:
            try:
                DISPLAY.reset()  # Reset display
                image = generate_image()
                set_display_flags(gen_image=False)
                if DISPLAY_IMAGE_ON_SCREEN.value:
                    show_on_physical_display(image)
                    set_display_flags(show_on_screen=False)
            except Exception as e:
                handle_error(e)
                set_display_flags(gen_image=False, show_on_screen=False)
        time.sleep(0.1)

def sensor_loop(sensor):
    while True:
        try:
            temperature, humidity, pressure = read_sensor.read_data(sensor)
            print(f"Sensor reading: {temperature}°C {pressure}hPa {humidity}%")
        except Exception as e:
            handle_error(e)
            sys.exit()  # Just exit on any error, systemd will restart if needed
        time.sleep(TIME_BETWEEN_READINGS)

def motion_loop(motion_line):
    while True:
        if motion_sensor.check_motion(motion_line) and not GENERATE_IMAGE.value:
            print('Motion detected - Triggering display update')
            set_display_flags(gen_image=True, show_on_screen=True)
            time.sleep(DISPLAY_TIMEOUT)
        time.sleep(0.1)

def main():
    global DISPLAY
    
    print("Initializing components...")
    sensor = read_sensor.init_sensor()
    DISPLAY = display_data.init_display()
    motion_line = motion_sensor.init_motion_sensor()
    print("Components initialized successfully")
    
    print("Taking initial sensor reading...")
    sensor.get_temperature()
    
    Thread(target=sensor_loop, args=(sensor,), daemon=True).start()
    Thread(target=display_loop, daemon=True).start()
    Thread(target=motion_loop, args=(motion_line,), daemon=True).start()
    
    print("Starting web server...")
    run_web_server.run(GENERATE_IMAGE, DISPLAY_IMAGE_ON_SCREEN)
    
if __name__ == "__main__":
    main()
