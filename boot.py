import network
import time
from machine import Pin
import webrepl
import ntptime  # Module for syncing time with NTP servers
import passwords

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
ssid = passwords.purcel_ssid  # Replace with your WiFi network name
password = passwords.purced_password  # Replace with your WiFi password
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

# Sync time with NTP server
try:
    print("Synchronizing time with NTP server...")
    ntptime.settime()  # Sync the Pico's RTC with an NTP server
    print("Time synchronized successfully!")
except Exception as e:
    print(f"Failed to synchronize time: {e}")

# Print the current time
current_time = time.localtime()
print(f"Current time: {current_time[0]}-{current_time[1]:02d}-{current_time[2]:02d} {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}")

# WebREPL Setup
webrepl.start(password=passwords.purcel_webrepl_password)