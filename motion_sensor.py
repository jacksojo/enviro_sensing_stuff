import RPi.GPIO as GPIO

MOTION_SENSOR_PIN = 17

def check_motion():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)
    return GPIO.input(MOTION_SENSOR_PIN) == GPIO.HIGH 