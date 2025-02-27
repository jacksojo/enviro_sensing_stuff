import RPi.GPIO as GPIO
import time

MOTION_SENSOR_PIN = 17
DEBOUNCE_TIME = 2  # seconds between valid triggers
REQUIRED_STABLE_TIME = 0.3  # seconds motion must be stable to trigger
last_trigger_time = 0

def init_motion_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    return MOTION_SENSOR_PIN

def check_motion(pin):
    global last_trigger_time
    current_time = time.time()
    
    # Check debounce period
    if current_time - last_trigger_time < DEBOUNCE_TIME:
        return False
        
    # Check if motion is stable
    if GPIO.input(pin) == GPIO.HIGH:
        time.sleep(REQUIRED_STABLE_TIME)
        if GPIO.input(pin) == GPIO.HIGH:  # Still high after waiting
            last_trigger_time = current_time
            return True
            
    return False