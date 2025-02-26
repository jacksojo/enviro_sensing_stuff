from flask import Flask, send_file
import time
from db_utils import execute_query, BME280_TABLE_DEF
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent

app = Flask(__name__)

#def get_data():
#    with app.app_context():
#        data = str(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc")[0])
#        return data

def run(display_queue):
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route("/image")
def serve_image():
    # Request new image generation
    app.display_queue.put(True)
    
    # Return the image file
    image_path = SCRIPT_DIR / "data" / "latest_image.png"
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Accessible on the local network
