import sqlite3
import os
import sys

# Define absolute path for the database
DB_PATH = "/home/jonathan/db/sensor_data.db"

if input('Do you really want to do this? It will wipe the existing db. enter "y" to continue') != 'y':
    print('canceling script')
    sys.exit()

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect to the database (it will be created if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS BME280_READINGS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    pressure REAL
)
""")

conn.commit()
conn.close()

print(f"Database created at {DB_PATH}")