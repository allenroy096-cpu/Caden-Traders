import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn_str = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(conn_str)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
