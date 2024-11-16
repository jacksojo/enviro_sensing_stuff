import pandas as pd
import glob
from datetime import date

todays_file = f'logs/temps_{date.today()}.log'

print("today's file", todays_file)
