import pandas as pd
import glob
from datetime import date

todays_file = f'logs/temps_{date.today()}.log'

f = open(todays_file, "r")

print(f.read()[0:100])

f.close()
