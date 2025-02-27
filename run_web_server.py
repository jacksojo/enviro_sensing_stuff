from flask import Flask, send_file
import time
from db_utils import execute_query, BME280_TABLE_DEF
from pathlib import Path
import importlib

SCRIPT_DIR = Path(__file__).parent
app = Flask(__name__)

def run():
    app.run(host='0.0.0.0', port=5000, debug=False)


@app.route("/image_file")
def serve_image_file():
    # Import and reload to get latest state
    import run_app
    importlib.reload(run_app)
    
    print('Image requested from web')
    run_app.set_display_flags(gen_image=True, show_on_screen=False)
    
    # Wait for image generation to complete
    start_time = time.time()
    while run_app.GENERATE_IMAGE:
        time.sleep(0.1)
        if time.time() - start_time > 2:  # Timeout after 2 seconds
            break
    
    # Return the image file
    image_path = SCRIPT_DIR / "data" / "latest_image.png"
    print('Image displayed on web')
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Accessible on the local network
