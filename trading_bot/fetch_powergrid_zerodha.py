from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")
access_token = os.getenv("KITE_ACCESS_TOKEN")  # Store your access token in .env for automation

db_path = 'trading_bot.db'
symbol = 'POWERGRID'
exchange = 'NSE'
interval = 'day'


today = datetime.today()
start_date = today - timedelta(days=365*5)

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# Get instrument token for POWERGRID
instruments = kite.instruments(exchange)
inst_token = None
for inst in instruments:
    if inst['tradingsymbol'] == symbol and inst['exchange'] == exchange:
        inst_token = inst['instrument_token']
        break
if not inst_token:
    raise Exception(f"Instrument token for {symbol} not found.")

# Fetch historical data
data = kite.historical_data(inst_token, start_date, today, interval)

# Store in DB
conn = sqlite3.connect(db_path)
c = conn.cursor()
for row in data:
    db_date = row['date'].strftime('%Y-%m-%d')
    open_ = row['open']
    high = row['high']
    low = row['low']
    close = row['close']
    volume = row['volume']
    c.execute('''
        INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (symbol + '.NS', db_date, open_, high, low, close, volume))
    print(f"Inserted {symbol}.NS for {db_date}: open={open_}, high={high}, low={low}, close={close}, volume={volume}")
conn.commit()
conn.close()
print("Done fetching and populating POWERGRID OHLC data from Zerodha for last 1 year.")
