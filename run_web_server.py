from flask import Flask, jsonify
import time
from db_utils import execute_query, BME280_TABLE_DEF

app = Flask(__name__)

data = jsonify(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Accessible on the local network
