import pandas as pd
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
    ['log_timestamp', 'string', lambda x: x],
    ['log_source', 'string', lambda x: x],
    ['log_level', 'string', lambda x: x],
    ['temperature_c', 'float', lambda x: x[:-1]],
    ['pressure_hpa', 'float', lambda x: x[:-3]],
    ['humidity_%', lambda x: x[:-1]],
    ['elevation_m', lambda x: x[:-1]],
    ['date', 'string', lambda x: x],
    ['time', 'string', lambda x: x]
]

df = pd.DataFrame([x.split() for x in raw], columns=[x[0] for x in schema])

#for i, c in enumerate(df.columns):
#    df[c] = df[c].apply(schema[i][2]).astype(schema[i][1])

high = df.loc[df['temperature_c'] == df['temperature_c'].max()]
low = df.loc[df['temperature_c'] == df['temperature_c'].max()]
current = df.loc[df.index == df.index.max()]

print(f"Today's high was {high['temperature_c']}C at {high['time']}")
print(f"Today's low was {low['temperature_c']}C at {low['time']}")
print(f"Right now the temperature is {current['temperature_c']}")
