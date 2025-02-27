import datetime
from db_utils import execute_query, BME280_TABLE_DEF

def get_temperature_data():
    q_template = """
      SELECT *
      FROM {table_name}
      WHERE TIMESTAMP >= '{start}' AND TIMESTAMP < '{end}'
      """
    today = datetime.date.today()
    this_time_yesterday = datetime.datetime.now() - datetime.timedelta(hours=23)
    tomorrow = today + datetime.timedelta(days=1)
    yesterday = today - datetime.timedelta(days=1)
    
    from_today = execute_query(q_template.format(
        start=str(today), 
        end=str(tomorrow), 
        table_name=BME280_TABLE_DEF['table_name']
    ))
    
    from_yesterday = execute_query(q_template.format(
        start=str(yesterday), 
        end=str(this_time_yesterday), 
        table_name=BME280_TABLE_DEF['table_name']
    ))

    return from_today, from_yesterday 