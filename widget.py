from PIL import Image, ImageDraw, ImageFont

class Widget:
    def __init__(self, x, y, width, height, color=(0,0,0,255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.image = Image.new('RGBA', (width, height), color)
        self.draw = ImageDraw.Draw(self.image)
        
    def add_text(self, text, font, x, y, line_width=0, line_color=(255,255,255,255), color=(255,255,255,255)):
        if line_width > 0:
            self.draw.line([(x, y+font.size+line_width), (x+font.getlength(text), y+font.size+line_width)], fill=line_color, width=line_width)
        self.draw.text((x, y), text, font=font, fill=color)
        
    def add_line(self, data, x1, y1, x2, y2, weight=1, show_y_range=True):
        if len(data) < 2:
            return
            
        min_y = min(data)
        max_y = max(data)
        y_range = max_y - min_y
        
        if show_y_range:
            self.draw.text((x1, y1), f"{max_y:.1f}", font=very_small_font, fill=(255,255,255,120))
            self.draw.text((x1, y2-very_small_font_height), f"{min_y:.1f}", font=very_small_font, fill=(255,255,255,120))
            
        x_step = (x2-x1)/(len(data)-1)
        scale = (y2-y1)/y_range if y_range > 0 else 1
        
        points = [(x1 + i*x_step, y2 - (val-min_y)*scale) for i, val in enumerate(data)]
        self.draw.line(points, fill=(255,255,255,255), width=weight)
        
    def publish(self):
        return self.image 