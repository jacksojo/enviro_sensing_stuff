import datetime
from PIL import Image, ImageDraw, ImageFont
from send_email import send_email
from st7789 import st7789

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

img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

class widget:
  
  def __init__(x,y,w,h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.background = Image.new("RGB", (w, h), color=(0, 0, 0))
    self.draw = ImageDraw.Draw(self.background)

  def add_text(text,font,x,y,color=(255,255,255):
    self.draw((x,y), text, font=font, fill=color)

  def add_image(im,x,y):
    return None

  def add_border(weight,color,rounded=True):
    return None


def read_data(q):

  return None




################
# I don't think this works properly
def terminate(error_text=' '):
    disp.reset()
    draw.text((5, 5), repr(error_text), font=font, fill=(255,255,255))
    disp.display(img)
    time.sleep(3)
    disp.display(Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0)))
    disp.set_backlight(0)
    sys.exit()



    
        ### update the background colour based on the current temp relative to the last 2 mins
        if len(recorded_temps) > 120:
            recorded_temps = recorded_temps[-120:]
    
        background_colour = set_background_colour(temperature)
    
        draw.rectangle((0, 0, WIDTH, HEIGHT), background_colour)
    
        ### add in the temperature text
        draw.text((5, 15), f"{temperature:05.2f}°C", font=font, fill=(255, 255, 255))
        draw.text((5, 55), f"{temp_from_api:05.2f}°C in town", font=small_font, fill=(255, 255, 255))
        draw.text((5, 95), f"{pressure:05.2f}hPa", font=font, fill=(255, 255, 255))
        draw.text((5, 155), f"{humidity:05.2f}%", font=font, fill=(255, 255, 255))
        draw.text((5, 215), f"{str(time.ctime())}", font=small_font, fill=(255, 255, 255))
        disp.display(img)
    
        time.sleep(60)
    except Exception as e:
        send_email(e)
        terminate(e)
