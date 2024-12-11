import datetime
import glob
import pandas as pd

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
    ['date', 'date', lambda x: x],
    ['time', 'timestamp', lambda x: x]
]

df = pd.DataFrame([x.split() for x in raw if len(x.split()) == len(schema))], columns=[x[0] for x in schema])
other_rows = [x for x in raw if len(x.split()) != len(schema)]

 

print(df.head())

