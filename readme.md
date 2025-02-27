# Environmental Sensor Display

A Raspberry Pi project that monitors temperature, humidity, and pressure using a BME280 sensor, displaying the data on both a physical LCD screen and web interface. The display activates when motion is detected.

## Features

- Real-time environmental monitoring (temperature, humidity, pressure)
- Motion-activated physical display
- Web interface for remote monitoring
- Historical data visualization
- SQLite database storage
- Automatic error reporting via email

## Hardware Requirements

- Raspberry Pi
- BME280 sensor (I2C interface)
- ST7789 LCD Display
- PIR Motion Sensor
- Appropriate wiring/connections

## Software Dependencies

- Python 3.7+
- Required Python packages:
  - Flask
  - Pillow
  - RPi.GPIO
  - smbus2
  - bme280

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables for email notifications:
   ```bash
   export EMAIL_USER="your_email@gmail.com" # The email to send from
   export EMAIL_PASSWORD="your_app_password" # The smtp password for the email
   export MY_EMAIL='recipient@email.com'
   ```

4. Initialize the database:
    ```bash
    python3 -c "import db_utils; db_utils.create_db()"
    ```

## Usage

1. Run the application:
   ```bash
   python3 run_app.py
   ```

The application will:
- Start collecting sensor data every 60 seconds
- Activate display when motion is detected
- Start a web server on port 5000

Access the web interface at: `http://your_pi_ip:5000/image`

## File Structure

- `run_app.py` - Main application entry point
- `display_data.py` - Display rendering and image generation
- `read_sensor.py` - BME280 sensor interface
- `motion_sensor.py` - PIR motion sensor interface
- `db_utils.py` - Database operations
- `run_web_server.py` - Flask web server
- `widget.py` - Display widget components
- `data_queries.py` - Database query functions

## Error Handling

Errors are logged to `logs/error_log.log` and critical errors trigger email notifications to the configured address.

## License

MIT License

