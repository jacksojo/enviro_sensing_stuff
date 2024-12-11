import datetime
import glob
import pandas as pd
import math
import re
import calendar

file_location = 'logs/'

files = glob.glob(file_location+'*')

files = [f for f in files if 'temps_2024-11' not in f]

raw = []

# Open the file in read mode
for file in files:
    with open(file, 'r') as f:
    # Read each line in the file
        for line in f:
            raw.append(line)

def fix_float(s):
    strip_s = re.sub("[^0-9].-", "", s)
    strip_s = strip_s[:8]
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
    ['date', 'datetime64[ns]', lambda x: x],
    ['time', 'string', lambda x: x]
]

df = pd.DataFrame([x.split() for x in raw if len(x.split()) == len(schema)], columns=[x[0] for x in schema])
for i, c in enumerate(df.columns):
    df[c] = df[c].apply(schema[i][2]).astype(schema[i][1])

other_rows = [x for x in raw if len(x.split()) != len(schema)]

date_ranges = []
for d in df['date'].sort_values().unique()[-7:]:
    date_min = df['temperature_c'].loc[df['date'] == d].min()
    date_max = df['temperature_c'].loc[df['date'] == d].max()
    date_ranges.append([d.date(), date_min, date_max])

week_min = min([x[1] for x in date_ranges])
week_max = max(x[2] for x in date_ranges)
degrees_diff = math.floor(week_max) - math.floor(week_min)

print(' ')
for deg in range(degrees_diff+1):
    row = '  '

    for d in date_ranges:
        if math.floor(d[2]) == math.floor(week_max) - deg:
            s = str(round(d[2],2))
        elif math.floor(d[1]) == math.floor(week_max) - deg:
            s = str(round(d[1],2))
        elif d[1] < week_max - deg and d[2] > week_max - deg:
            s = '  |'
        else:
            s = ''
        row += s
        row += ''.join([' ' for x in range(12-len(s))])
        if math.floor(week_max) - deg == 0:
            print('0')
            row.replace('  ', '. ')
    print(row)
print(' ')
row = '  '
for d in date_ranges:
    weekday = calendar.day_name[d[0].weekday()]
    row += weekday
    row += ''.join([' ' for x in range(12-len(weekday))])
print(row)

row = '  '
for d in date_ranges:
    datestring = str(d[0])
    row += datestring
    row += ''.join([' ' for x in range(12-len(datestring))])
print(row)
        
