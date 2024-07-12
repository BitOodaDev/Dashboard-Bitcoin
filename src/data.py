import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os

def load_env():
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
    load_dotenv(dotenv_path)

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

def load_data():
    conn = get_snowflake_connection()
    query = "SELECT * FROM btc_daily ORDER BY TIMESTAMP"
    df = pd.read_sql(query, conn)
    df['Time'] = pd.to_datetime(df['TIMESTAMP'])
    conn.close()
    return df
