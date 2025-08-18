
from nsepy import get_history
import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'trading_bot.db'
SYMBOL = 'POWERGRID'

# Set date range for last 1 year
today = datetime.today()
start_date = today - timedelta(days=365)

def fetch_and_store():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Fetch daily data for last 1 year
    data = get_history(symbol=SYMBOL,
                      start=start_date,
                      end=today,
                      index=False)
    for idx, row in data.iterrows():
        db_date = idx.strftime('%Y-%m-%d')
        open_ = row['Open']
        high = row['High']
        low = row['Low']
        close = row['Close']
        volume = row['Volume']
        c.execute('''
            INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (SYMBOL + '.NS', db_date, open_, high, low, close, volume))
        print(f"Inserted {SYMBOL}.NS for {db_date}: open={open_}, high={high}, low={low}, close={close}, volume={volume}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_and_store()
    print("Done fetching and populating POWERGRID historical data for last 1 year.")
