import datetime
from PIL import Image, ImageDraw, ImageFont
from send_email import send_email
import st7789

# Initialise the st7789
disp = st7789.ST7789(
        height=240,
        rotation=90,
        port=0,
        cs=st7789.BG_SPI_CS_FRONT, 
        dc=9,
        backlight=19,  
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0,
    )


disp.begin()

LARGE_FONT = ImageFont.truetype('/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 50)
SMALL_FONT = ImageFont.truetype('/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf', 20)

WIDTH = disp.width
HEIGHT = disp.height

img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 255))
draw = ImageDraw.Draw(img)

class widget:
  
  def __init__(x,y,w,h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.image = Image.new("RGB", (w, h), color=(0, 0, 0))
    self.draw = ImageDraw.Draw(self.image)

  def add_text(text,font,x,y,color=(255,255,255)):
    self.draw.text((x,y), text, font=font, fill=color)

  def add_image(im,x,y):
    self.image.paste(im, (x,y))

  def add_border(weight,color,rounded=True):
    # need to do this before adding other elements
    self.image = Image.new("RGB", (self.w, self.h), color=color)
    #### need to add something here
    return None

  def publish():
    img.paste(self.image, (self.x, self.y))

top_left = widget(5, 5, 40, 40)
top_left.add_text('-10.00', LARGE_FONT, 10, 10)
top_left.publish()

img.save("/home/jonathan/db/latest_image.png")

def read_data(q):

  return None
