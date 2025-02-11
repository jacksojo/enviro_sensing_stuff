from flask import Flask, send_file
import time
from db_utils import execute_query, BME280_TABLE_DEF

def run_web_server():

    app = Flask(__name__)

    #def get_data():
    #    with app.app_context():
    #        data = str(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc")[0])
    #        return data

    @app.route("/image")
    def serve_image():
        image_path = "/home/jonathan/db/latest_image.png"
        return send_file(image_path, mimetype='image/png')

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000, debug=True)  # Accessible on the local network
