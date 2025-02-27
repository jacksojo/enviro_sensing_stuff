from flask import Flask, send_file
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
app = Flask(__name__)

def run(generate_image, display_image):
    app.generate_image = generate_image
    app.display_image = display_image
    app.run(host='0.0.0.0', port=5000, debug=False)

@app.route("/image")
def serve_image():
    print('Image requested from web')
    app.generate_image.value = True
    
    # Wait for image generation to complete
    start_time = time.time()
    while app.generate_image.value:
        time.sleep(0.1)
        if time.time() - start_time > 2:  # Timeout after 2 seconds
            break
    
    image_path = SCRIPT_DIR / "data" / "latest_image.png"
    print('Image displayed on web')
    return send_file(image_path, mimetype='image/png')