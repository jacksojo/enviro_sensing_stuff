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

raw_font = '/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf'
large_font_height = 110
small_font_height = 45
very_small_font_height=20
buffer = 5

large_font = ImageFont.truetype(raw_font, large_font_height)
small_font = ImageFont.truetype(raw_font, small_font_height)
very_small_font = ImageFont.truetype(raw_font, very_small_font_height)

WIDTH = disp.width
HEIGHT = disp.height

img = Image.new("RGB", (WIDTH, HEIGHT), color=(100, 100, 100))
draw = ImageDraw.Draw(img)

class widget:
  
  def __init__(self,x,y,w,h,color=(0,0,0)):
    self.x = x
    self.y = y
    self.width = w
    self.height = h
    self.image = Image.new("RGB", (w, h), color=color)
    self.draw = ImageDraw.Draw(self.image)

  def add_text(self,text,font,x,y,color=(255,255,255)):
    text = self.draw.text((x,y-10), text, font=font, fill=color)
    return text

  def add_image(self,im,x,y):
    self.image.paste(im, (x,y))

  def add_border(self,weight,color,rounded=True):
    # need to do this before adding other elements
    self.image = Image.new("RGB", (self.w, self.h), color=color)
    #### need to add something here
    return None
  
  def add_line(self, data, start_x, start_y, w, h, color=(0,0,0), weight=3, show_y_range=True):

    max_x = max([d[0] for d in data])
    min_x = min([d[0] for d in data])
    max_y = max([d[1] for d in data])
    min_y = min([d[1] for d in data])

    if show_y_range:
      max_y_str = str(max_y).split('.')[0]+'.'+str(max_y).split('.')[1][0]
      min_y_str = str(min_y).split('.')[0]+'.'+str(min_y).split('.')[1][0]
      self.draw.text((start_x, start_y), max_y_str, font=very_small_font)
      self.draw.text((start_y, start_y+h-very_small_font_height/2), min_y_str, font=very_small_font)

      space_used_by_labels = max([very_small_font.getlength(max_y_str), very_small_font.getlength(min_y_str)])+buffer*2

      start_x = start_x+space_used_by_labels
      w = w - space_used_by_labels

    normed_data = []
    for x, y in data:
      x = start_x + ((x - min_x) / (max_x - min_x) * w)
      y = start_y + h - ((y - min_y) / (max_y - min_y) * h)
      normed_data.append((x, y))

    self.draw.line(normed_data,fill=color,width=weight)

  def publish(self):
    img.paste(self.image, (self.x, self.y))


### Temperature widget
test_temp = -12.34
big = str(test_temp).split('.')[0]
big_w = large_font.getlength(big)
small = '.'+str(test_temp).split('.')[1][:2]+'°'
small_w = small_font.getlength(small)

temp_widget = widget(buffer,buffer,int(WIDTH)-buffer*2,int(HEIGHT/1.6)-buffer*2,(190,190,160))
temp_widget.add_text(big,large_font,temp_widget.width-big_w-small_w-buffer,temp_widget.height-large_font_height+20)
temp_widget.add_text(small,small_font,temp_widget.width-small_w-buffer,temp_widget.height-small_font_height)

## dummy data
temp_widget.add_line([(0.0,0.0),(1.0,1.0),(2.0,1.0),(3.0,2.0),(5.0,2.0),(7.0,3.0)],buffer,buffer,temp_widget.width-10,50)
temp_widget.publish()


### Humidity widget
test_hum = 69.78
test_pressure = 864.3
pre = str(test_pressure)
hum = str(test_hum)+'%'
pre_unit = 'hpa'


hum_widget = widget(buffer,temp_widget.height+buffer*2,int(WIDTH/1.7)-buffer*2,int(HEIGHT-temp_widget.height)-buffer*3,(150,120,120))
hum_widget.add_text(pre,small_font,buffer,buffer)
hum_widget.add_text(pre_unit, very_small_font, small_font.getlength(pre)+buffer*2, small_font_height-very_small_font_height-buffer)
hum_widget.add_text(hum,small_font,buffer,small_font_height)
hum_widget.publish()


img.save("/home/jonathan/db/latest_image.png")
