import time
import utime
from machine import Pin, I2C
import bme280_driver
import network
from logger import Logger
import socket
import json
from machine import Pin
import gc
import passwords


# Constants
TIME_BETWEEN_READINGS = 3600  # seconds aka an hour
TIME_BETWEEN_FINE_GRAIN_READINGS = 60 # seconds
NUMBER_OF_FINE_GRAIN_READINGS = 10 # number of fine grain readings to store
MAX_CONNECTIONS = 3  # Maximum number of connection attempts

# Initialize logger
logger = Logger()

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

# Store readings
today_readings = []
yesterday_readings = []
fine_grain_readings = []
date_today = utime.localtime()[2]
last_reading_time = 0
last_fine_grain_reading_time = 0
latest_reading = None  # Store the most recent reading
latest_fine_grain_reading = None  # Store the most recent fine grain reading

# Function for visual feedback
def blink_led(times, delay=0.2):
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)

def take_reading():
    global today_readings, latest_reading
    try:
        sensor.set_power_mode(bme280_driver.BME280_FORCED_MODE)
        utime.sleep(1)  # Wait for the measurement to complete
        readings = sensor.get_measurement()
        readings['timestamp'] = utime.time()
        today_readings.append(readings)
        latest_reading = readings  # Update the latest reading
        blink_led(1,1)
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
        time.sleep(1)
    
    # Check connection status
    if wlan.status() != 3:
        logger.log(f"WiFi connection failed. Status: {wlan.status()}", "ERROR")
        return None
    else:
        ip_address = wlan.ifconfig()[0]
        logger.log(f"Connected to WiFi. IP address: {ip_address}")
        return ip_address

def generate_json_response(t_readings, y_readings):
    
    summary_temps = {
        "current_temperature": t_readings[-1]['temperature'],
        "max_temperature": max([t['temperature'] for t in t_readings]),
        "min_temperature": min([t['temperature'] for t in t_readings]),
        }
        
    # Convert readings to JSON
    def format_readings(readings):
        readings.reverse()
        return [{"timestamp": r['timestamp'], 
                 "temperature": r['temperature'], 
                 "humidity": r['humidity'], 
                 "pressure": r['pressure']} for r in readings]
                
    #Create the JSON object
    response_data = {
        "summary": summary_temps,
        "today": format_readings(t_readings),
        "yesterday": format_readings(y_readings)
    }

    # Convert to JSON string
    response_json = json.dumps(response_data)

    # Create the HTTP response
    response = f"""HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{response_json}"""
    return response

def main():
    global date_today, yesterday_readings, today_readings, last_reading_time, latest_reading
    logger.log("Starting environmental monitor...")
    
    # Connect to WiFi
    ssid = passwords.purcel_ssid  # Replace with your WiFi network name
    password = passwords.purcel_password  # Replace with your WiFi password
    ip_address = connect_to_wifi(ssid, password)
    if not ip_address:
        logger.log("Failed to connect to WiFi. Exiting.", "ERROR")
        return

    # Create web server
    try:
        addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(MAX_CONNECTIONS)
        logger.log(f"Web server running at http://{ip_address}:8080/", "INFO")
    except Exception as e:
        logger.log(f"Failed to start web server: {e}", "ERROR")
        return

    # Main loop
    while True:
        try:
            current_time = utime.time()
            
            # Check if it's time for a new reading
            if current_time - last_reading_time >= TIME_BETWEEN_READINGS:
                last_reading_time = current_time
                take_reading()
            
            # Check for new day
            if utime.localtime()[2] != date_today:
                date_today = utime.localtime()[2]
                yesterday_readings = today_readings
                today_readings = []
            
            # Handle web connections    
            try:
                # Use a shorter, non-blocking accept with a manual timeout
                s.setblocking(False)
                try:
                    client, addr = s.accept()
                except OSError as e:
                    # No connection available
                    if e.args[0] == 11:  # EAGAIN error
                        utime.sleep(0.1)
                        continue
                    raise
                
                # Log connection details
                logger.log(f"Connection from {addr}", "INFO")
                
                try:
                    # Implement manual timeout for request
                    client.setblocking(False)
                    start_time = utime.time()
                    
                    # Wait for data with timeout
                    request = b''
                    while True:
                        try:
                            chunk = client.recv(1024)
                            if not chunk:
                                break
                            request += chunk
                            if b'\r\n\r\n' in request:  # Complete HTTP request
                                break
                        except OSError as e:
                            if e.args[0] == 11:  # EAGAIN error
                                # Check if we've exceeded timeout
                                if utime.time() - start_time > 2:
                                    logger.log("Connection timeout", "WARN")
                                    break
                                utime.sleep(0.1)
                                continue
                            raise
                    
                    # Only log and process if request is not empty
                    if request:
                        # Log request details
                        logger.log(f"Received request: {request}", "DEBUG")
                        blink_led(2, .1)
                        
                        # Check if it's a favicon request
                        if b'/favicon.ico' in request:
                            # Send a minimal response for favicon
                            client.send(b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n")
                        else:
                            # Generate response
                            response = generate_json_response(today_readings, yesterday_readings)
                            
                            # Send response
                            client.send(response.encode('utf-8'))
                
                except Exception as req_error:
                    # Only log non-EAGAIN errors
                    if not (isinstance(req_error, OSError) and req_error.args[0] == 11):
                        logger.log(f"Request handling error: {req_error}", "ERROR")
                
                finally:
                    # Always close the client connection
                    client.close()
            
            except Exception as conn_error:
                # Only log non-EAGAIN connection errors
                if not (isinstance(conn_error, OSError) and conn_error.args[0] == 11):
                    logger.log(f"Connection error: {conn_error}", "ERROR")
            
            # Short sleep to prevent tight loop
            utime.sleep(0.1)

            # Free up memory
            gc.collect()
        
        except Exception as e:
            logger.log(f"Unexpected error: {e}", "ERROR")
            utime.sleep(5)

if __name__ == '__main__':
    main()