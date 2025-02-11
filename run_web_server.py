from flask import Flask, send_from_directory
import time
from db_utils import execute_query, BME280_TABLE_DEF

app = Flask(__name__)

def get_data():
    with app.app_context():
        data = str(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc")[0])
        return data

def get_image():
    return send_from_directory("static", "/home/jonathan/db/latest_image.png")

@app.route("/")
def home():
    return get_image()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Accessible on the local network
