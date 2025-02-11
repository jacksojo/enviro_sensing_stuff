from flask import Flask, jsonify
import time
from db_utils import execute_query, BME280_TABLE_DEF

app = Flask(__name__)

def get_data():
    with app.app_context():
        data = str(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc"))
        print(data)
        return data

@app.route("/")
def home():
    x = get_data()

    return f"Data: {x}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Accessible on the local network
