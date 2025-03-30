import utime
from machine import Pin, I2C
import bme280_driver
import network
from logger import Logger
import json
from machine import Pin
import passwords
from umqtt_simple import MQTTClient  # MicroPython MQTT library


# Constants
TIME_BETWEEN_READINGS = 60  # seconds
WIFI_SSID = passwords.purcel_ssid  # Replace with your WiFi network name
WIFI_PASSWORD = passwords.purcel_password  # Replace with your WiFi password
THINGER_USERNAME = passwords.thinger_username
THINGER_DEVICE_ID = passwords.thinger_device_id
THINGER_DEVICE_CREDENTIAL = passwords.thinger_device_credential
THINGER_BROKER = passwords.thinger_broker
THINGER_PORT = passwords.thinger_port

# Initialize logger
logger = Logger()

# Setup LED
led = Pin("LED", Pin.OUT)  # Pico's built-in LED

# Initialize hardware
try:
    i2c = I2C(1, sda=Pin(2), scl=Pin(3))
    sensor = bme280_driver.BME280_I2C(i2c=i2c)
    sensor.set_measurement_settings({
        'osr_h': bme280_driver.BME280_OVERSAMPLING_1X,
        'osr_p': bme280_driver.BME280_OVERSAMPLING_1X,
        'osr_t': bme280_driver.BME280_OVERSAMPLING_1X,
        'filter': bme280_driver.BME280_FILTER_COEFF_OFF,
        'standby_time': bme280_driver.BME280_STANDBY_TIME_1000_MS
    })
    logger.log("Hardware initialization successful")
except Exception as e:
    logger.log(f"Hardware initialization failed: {e}", "ERROR")
    raise

# Function for visual feedback
def blink_led(times, delay=0.2):
    for _ in range(times):
        led.on()
        utime.sleep(delay)
        led.off()
        utime.sleep(delay)

def take_reading():
    try:
        sensor.set_power_mode(bme280_driver.BME280_FORCED_MODE)
        utime.sleep(1)  # Wait for the measurement to complete
        readings = sensor.get_measurement()
        readings['timestamp'] = utime.localtime()
        blink_led(1, 1)
        logger.log(f"New reading: Temp={readings['temperature']}C, Humidity={readings['humidity']}%, Pressure={readings['pressure']}hPa")
        return readings
    except Exception as e:
        logger.log(f"Failed to take reading: {e}", "ERROR")
        raise

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Attempt to connect
    wlan.connect(ssid, password)
    
    # Wait for connection with timeout
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        logger.log(f'Waiting for WiFi connection... (attempts left: {max_wait})')
        utime.sleep(1)
    
    # Check connection status
    if wlan.status() != 3:
        logger.log(f"WiFi connection failed. Status: {wlan.status()}", "ERROR")
        return None
    else:
        ip_address = wlan.ifconfig()[0]
        logger.log(f"Connected to WiFi. IP address: {ip_address}")
        return ip_address

def connect_to_mqtt():
    """
    Connect to the Thinger.io MQTT broker.
    """
    try:
        mqtt_client = MQTTClient(THINGER_DEVICE_ID, THINGER_BROKER, port=THINGER_PORT, user=THINGER_USERNAME, password=THINGER_DEVICE_CREDENTIAL)
        mqtt_client.connect()
        logger.log("Connected to Thinger.io MQTT broker")
        return mqtt_client
    except Exception as e:
        logger.log(f"Failed to connect to MQTT broker: {e}", "ERROR")
        raise

def send_to_thinger(mqtt_client, readings):
    """
    Publish sensor readings to Thinger.io via MQTT.
    """
    try:
        topic = f"{THINGER_USERNAME}/devices/{THINGER_DEVICE_ID}/data"
        payload = json.dumps(readings)
        mqtt_client.publish(topic, payload)
        logger.log(f"Published data to Thinger.io: {payload}")
    except Exception as e:
        logger.log(f"Failed to publish data to Thinger.io: {e}", "ERROR")
        raise

def main():
    logger.log("Starting environmental monitor...")
    
    # Connect to WiFi
    ip_address = connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)
    if not ip_address:
        logger.log("Failed to connect to WiFi. Exiting.", "ERROR")
        return

    # Connect to MQTT broker
    mqtt_client = connect_to_mqtt()

    # Main loop
    while True:
        try:            
            # Take a reading
            reading = take_reading()

            # Send the reading to Thinger.io
            send_to_thinger(mqtt_client, reading)

            # Wait for the next reading
            utime.sleep(TIME_BETWEEN_READINGS)
            
        except Exception as e:
            logger.log(f"Unexpected error: {e}", "ERROR")
            utime.sleep(5)

if __name__ == '__main__':
    main()