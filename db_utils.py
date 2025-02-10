import sqlite3
import os
import sys

# Define absolute path for the database
DB_PATH = "/home/jonathan/db/sensor_data.db"

# Define Schema(s)
BME280 = {
    'table_name': 'BME280_READINGS'
    'schema': {
        'id':'INTEGER PRIMARY KEY AUTOINCREMENT'
        , 'timestamp': 'DATETIME'
        , 'temperature': 'REAL'
        , 'humidity': 'REAL'
        , 'pressure': 'REAL'
    }
}

def create_db()
    ### call this func from an external shell using 'python3 -c import db_scripts; dbscripts.create_db()'
    if input('Do you really want to do this? It will wipe the existing db if it already exists. enter "y" to continue: ') != 'y':
        print('canceling script')
        sys.exit()

    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.close()

    print(f"Database created at {DB_PATH}")
    


def create_table(table_def)
    schema_string = '\n, '.join(['{k} {v}' for k, v in table_def['schema'].items()])
    
    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_def['table_name']} ({schema_string})")
    conn.commit()
    conn.close()

    print(f"table {table_def['table_name']} created at {DB_PATH} with schema {schema_string}")


def write_row_to_db(table_def, row):
    
    if row.keys() != table_df['schema'].keys():
        print(f'incoming row does not match schema!')
        print(f'row keys = {row.keys()}')
        print(f'schema keys = {table_df['schema'].keys()}')
        sys.exit()
    
    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO {table_df['table_name']} ({", ".join(row.keys())}) VALUES {", ".join(row.values())}')

    # Commit and close
    conn.commit()
    conn.close()
