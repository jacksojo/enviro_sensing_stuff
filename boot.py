# boot.py
import network
import time
from machine import Pin
import webrepl

# Setup LED
led = Pin("LED", Pin.OUT)  # Pico's built-in LED

# Function for visual feedback
def blink_led(times, delay=0.2):
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)

# Power-on indicator
led.on()
time.sleep(1)
led.off()

# Setup WiFi
ssid = '___'
password = '___'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Blink while trying to connect
while not wlan.isconnected():
    blink_led(1, 0.5)
    time.sleep(0.5)

# Connected - rapid blinks
blink_led(5, 0.1)
print('Network Config:', wlan.ifconfig())

# WebREPL Setup
webrepl.start(password='Monster1')