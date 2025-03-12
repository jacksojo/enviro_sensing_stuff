import st7789
import display_data
from PIL import Image

display = display_data.init_display()

path = r'data/latest_image.png'

img = Image.open(path)

if image:
  print('image found')
else:
  print('image read error').convert("RGB")
  
pixels = img.load()

display_data.display_image_on_screen(display, img)

