# Environmental Sensor (Pico W Version)

A Raspberry Pi Pico W project that monitors temperature, humidity, and pressure using a BME280 sensor and serves the data via a web interface.

## Features
- Real-time environmental monitoring (temperature, humidity, pressure)
- Simple web interface for remote monitoring
- Last 24 hours of readings stored in memory

## Hardware Requirements
- Raspberry Pi Pico W
- BME280 sensor (I2C interface)
- Appropriate wiring/connections

## Installation
1. Install MicroPython on your Pico W.
2. Copy all .py files to the Pico W.
3. Configure WiFi settings in `boot.py`.

## Pin Connections
- BME280: SDA -> GP2, SCL -> GP3

## Detailed Wiring Instructions

### Power Connections
- BME280 VIN -> Pico 3.3V
- BME280 GND -> Pico GND

### Data Connections
1. BME280 Sensor (I2C)
   - SDA -> GP2 (I2C1 SDA)
   - SCL -> GP3 (I2C1 SCL)

## Usage
The application will:
- Start collecting sensor data.
- Start a web server on port 80.

Access the temperature data at: `http://<your_pico_ip>/data`