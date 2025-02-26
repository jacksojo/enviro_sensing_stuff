from flask import Flask, send_file
import time
from db_utils import execute_query, BME280_TABLE_DEF
from pathlib import Path
from run_app import generate_image
SCRIPT_DIR = Path(__file__).parent

app = Flask(__name__)

#def get_data():
#    with app.app_context():
#        data = str(execute_query(f"select * from {BME280_TABLE_DEF['table_name']} order by timestamp desc")[0])
#        return data

def run():
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route("/image")
def serve_image():
    # Import here to avoid circular imports
    from run_app import set_display_flags
    
    # Request new image generation without showing on display
    print('image requested from web')
    set_display_flags(gen_image=True)
    
    # Wait briefly for image generation
    time.sleep(1.2)
    
    # Return the image file
    image_path = SCRIPT_DIR / "data" / "latest_image.png"
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Accessible on the local network
