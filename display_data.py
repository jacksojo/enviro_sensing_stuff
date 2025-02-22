import datetime
from PIL import Image, ImageDraw, ImageFont
from send_email import send_email
import st7789
from db_utils import execute_query, BME280_TABLE_DEF
import sys

raw_font = '/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf'
large_font_height = 120
small_font_height = 42
very_small_font_height=20
buffer = 5

large_font = ImageFont.truetype(raw_font, large_font_height)
small_font = ImageFont.truetype(raw_font, small_font_height)
very_small_font = ImageFont.truetype(raw_font, very_small_font_height)

h_divider = .6
v_divider = .75



def init_display():
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
  return disp

def build_image(disp):

  disp_width = disp.width
  disp_height = disp.height

  img = Image.new("RGBA", (disp_width, disp_height), color=(235, 235, 235, 255))
  draw = ImageDraw.Draw(img)

  class widget:
    
    def __init__(self,x,y,w,h,color=(0,0,0)):
      self.x = x
      self.y = y
      self.width = w
      self.height = h
      self.image = Image.new("RGB", (w, h), color=color)
      self.draw = ImageDraw.Draw(self.image)

    def add_text(self,text,font,x,y,color=(255,255,255,255), line_width=0, line_color='black'):
      self.draw.text((x,y-10), text, font=font, fill=color, stroke_width=line_width, stroke_fill=line_color)

    def add_image(self,im,x,y):
      self.image.paste(im, (x,y))

    ### unused and untested
    def add_border(self,weight,color,rounded=True):
      # need to do this before adding other elements
      self.image = Image.new("RGBA", (self.w, self.h), color=color)
      #### need to add something here
      return None
    
    def add_line(self, data, start_x, start_y, w, h, color=(0,0,0,255), weight=3, show_y_range=True, shadow_data=None):

      max_x = max([d[0] for d in data])
      if shadow_data:
        max_x = max_x + 3600 ## add one hour
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

      def norm_data(d):
        normed = []
        for x, y in d:
          x = start_x + ((x - min_x) / (max_x - min_x) * w)
          y = start_y + h - ((y - min_y) / (max_y - min_y) * h)
          normed.append((x, y))
        return normed

      if shadow_data:
        shadow_line = norm_data(shadow_data)
        self.draw.line(shadow_line,fill=(170,170,170,170),width=2)

      main_line = norm_data(data)
      self.draw.line(main_line,fill=color,width=weight)

    def publish(self):
      img.paste(self.image, (self.x, self.y))

  def get_data():
    q_template = """
      SELECT *
      FROM {table_name}
      WHERE TIMESTAMP >= '{start}' AND TIMESTAMP < '{end}'
      """
    today = datetime.date.today()
    this_time_yesterday = datetime.datetime.now() - datetime.timedelta(hours=23)
    tomorrow = today + datetime.timedelta(days=1)
    yesterday = today - datetime.timedelta(days=1)
    
    from_today = execute_query(q_template.format(start=str(today), end=str(tomorrow), table_name=BME280_TABLE_DEF['table_name']))
    from_yesterday = execute_query(q_template.format(start=str(yesterday), end=str(this_time_yesterday), table_name=BME280_TABLE_DEF['table_name']))

    return from_today, from_yesterday

  def transform_data(d, m, offset_day=False):
    offset = 86400 if offset_day else 0
    return [(datetime.datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S.%f').timestamp() + offset, r[m]) for r in d]
    
  data_today, data_yesterday = get_data()

  ## if we only have 1 row of data then skip this image
  #if len(data_today) < 2:
    #sys.exit()

  current_temp = data_today[-1]['temperature']
  current_pressure = data_today[-1]['pressure']
  current_humidity = data_today[-1]['humidity']
  current_timestamp = data_today[-1]['timestamp']
  temps_today = transform_data(data_today, 'temperature')
  hum_today = transform_data(data_today, 'humidity')
  pres_today = transform_data(data_today, 'pressure')
  temps_yesterday = transform_data(data_yesterday, 'temperature', offset_day=True)


  ### Temperature widget
  big = str(current_temp).split('.')[0]
  big_w = large_font.getlength(big)
  small = '.'+str(current_temp).split('.')[1][:2]+'°'
  small_w = small_font.getlength(small)

  temp_widget = widget(buffer,buffer,int(disp_width)-buffer*2,int(disp_height*h_divider)-buffer,(218,200,151,255))
  temp_widget.add_line(temps_today,buffer,buffer,temp_widget.width-10,60,color=(255,255,255,255),shadow_data=temps_yesterday)
  temp_widget.add_text(big,large_font,temp_widget.width-big_w-small_w-2,temp_widget.height-large_font_height+10,color=(255,255,255,128),line_width=2)
  temp_widget.add_text(small,small_font,temp_widget.width-small_w-2,temp_widget.height-small_font_height+5, line_width=1)
  temp_widget.publish()


  ### Humidity widget
  pre = str(current_pressure).split('.')[0]+'.'+str(current_pressure).split('.')[1][0]
  hum = str(current_humidity).split('.')[0]+'.'+str(current_humidity).split('.')[1][0:2]
  pre_unit = 'hpa'
  hum_unit = '%'


  hum_widget = widget(buffer,temp_widget.height+buffer*2,int(disp_width*v_divider)-buffer,int(disp_height-temp_widget.height)-buffer*3,(121,150,168,255))
  hum_widget.add_line(pres_today,0,0,hum_widget.width,hum_widget.height/2,weight=1,show_y_range=False)
  hum_widget.add_text(pre,small_font,buffer,buffer, line_width=1, color=(255,255,255,120))
  hum_widget.add_text(pre_unit, very_small_font, small_font.getlength(pre)+buffer*2, small_font_height-very_small_font_height+buffer,color=(255,255,255,120))
  hum_widget.add_line(hum_today,0,hum_widget.height/2,hum_widget.width,hum_widget.height/2,weight=1,show_y_range=False)
  hum_widget.add_text(hum,small_font,buffer,hum_widget.height/2+buffer, line_width=1, color=(255,255,255,120))
  hum_widget.add_text(hum_unit, very_small_font, small_font.getlength(hum)+buffer*2, small_font_height+very_small_font_height+buffer, color=(255,255,255,120))
  hum_widget.publish()

  
  ### Time widget
  hours = str(current_timestamp.split(' ')[1].split(':')[0])
  hours_w = small_font.getlength(hours)
  minutes = str(current_timestamp.split(' ')[1].split(':')[1])
  minutes_w = small_font.getlength(minutes)
  
  time_widget = widget(hum_widget.width+buffer*2, temp_widget.height+buffer*2, disp_width-hum_widget.width-buffer*3, disp_height-temp_widget.height-buffer*3,color=(100,100,100,0))
  time_widget.add_text(hours, small_font, time_widget.width/2-hours_w/2, time_widget.height*.25-small_font_height*.35, line_width=1)
  time_widget.add_text(minutes, small_font, time_widget.width/2-minutes_w/2, time_widget.height*.75-small_font_height*.35, line_width=1, line_color=(150,150,150,255))
  time_widget.publish() 

  return img

def display_image_on_screen(disp, image):
  disp.display(image)

def save_image(image):
  image.save("./data/latest_image.png")
