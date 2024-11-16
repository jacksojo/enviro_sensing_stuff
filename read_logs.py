import pandas as pd
import glob
from datetime import date

todays_file = f'logs/temps_{date.today()}.log'

raw = []

# Open the file in read mode
with open(todays_file, 'r') as file:
    # Read each line in the file
    for line in file:
        raw.append(line)

file.close()

schema = [
   #['col_name', 'datetype', cleaning_func] 
    ['log_timestamp', 'string', None],
    ['log_source', 'string', None],
    ['log_level', 'string', None],
    ['temperature_c', 'float', lambda x: x[:-1]],
    ['pressure_hpa', 'float', lambda x: x[:-3]],
    ['humidity_%', lambda x: x[:-1]],
    ['elevation_m', lambda x: x[:-1]],
    ['date', 'string', None],
    ['time', 'string', None]
]

df = pd.DataFrame([x.split() for x in raw], columns=[x[0] for x in schema])

print(df.tail())
