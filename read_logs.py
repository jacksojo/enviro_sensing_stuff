import pandas as pd
from datetime import date
import re

todays_file = f'logs/temps_{date.today()}.log'

raw = []

# Open the file in read mode
with open(todays_file, 'r') as file:
    # Read each line in the file
    for line in file:
        raw.append(line)

file.close()

def fix_float(s):
    strip_s = re.sub("[^0-9]", "", s)
    if s[0] == '-':
        return float(strip_s) * -1
    else:
        return float(strip_s)

schema = [
   #['col_name', 'datetype', cleaning_func] 
    ['log_timestamp', 'string', lambda x: x],
    ['log_source', 'string', lambda x: x],
    ['log_level', 'string', lambda x: x],
    ['temperature_c', 'float', fix_float],
    ['pressure_hpa', 'float', fix_float],
    ['humidity_%', 'float', fix_float],
    ['elevation_m', 'float', fix_float],
    ['date', 'string', lambda x: x],
    ['time', 'string', lambda x: x]
]

df = pd.DataFrame([x.split() for x in raw], columns=[x[0] for x in schema])

for i, c in enumerate(df.columns):
    df[c] = df[c].apply(schema[i][2]).astype(schema[i][1])

high = df.loc[df['temperature_c'] == df['temperature_c'].max()]
low = df.loc[df['temperature_c'] == df['temperature_c'].min()]
current = df.loc[df.index == df.index.max()]

print(f"Today's high was {high['temperature_c'].values[0]}C at {high['time'].values[0]}")
print(f"Today's low was {low['temperature_c'].values[0]}C at {low['time'].values[0]}")
print(f"Right now the temperature is {current['temperature_c'].values[0]} at {current['time'].values[0]}")
