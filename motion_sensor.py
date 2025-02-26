import gpiod
from gpiod.line import Direction, Value

MOTION_SENSOR_PIN = 17  # Adjust this to match your GPIO pin

def init_motion_sensor():
    chip = gpiod.Chip('gpiochip0')
    motion_line = chip.get_line(MOTION_SENSOR_PIN)
    config = gpiod.LineSettings(direction=Direction.INPUT)
    motion_line.request(consumer="motion_sensor", config=config)
    return motion_line

def check_motion(motion_line):
    return motion_line.get_value() == Value.ACTIVE 