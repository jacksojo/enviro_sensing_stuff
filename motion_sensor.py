import RPi.GPIO as GPIO

MOTION_SENSOR_PIN = 17  # Adjust this to match your GPIO pin

def init_motion_sensor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)
    return MOTION_SENSOR_PIN

def check_motion(pin):
    return GPIO.input(pin) == GPIO.HIGH 