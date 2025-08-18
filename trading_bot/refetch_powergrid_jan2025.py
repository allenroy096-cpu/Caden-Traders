from nsepython import nsefetch
import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'trading_bot.db'
SYMBOL = 'POWERGRID.NS'
NSE_SYMBOL = 'POWERGRID'

# Dates for the week of Jan 27, 2025 to Feb 1, 2025
start_date = datetime(2025, 1, 27)
end_date = datetime(2025, 2, 1)

def fetch_and_store():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        try:
            url = f'https://www.nseindia.com/api/quote-equity?symbol={NSE_SYMBOL}'
            data = nsefetch(url)
            price_info = data.get('priceInfo', {})
            open_ = price_info.get('open')
            high = price_info.get('intraDayHighLow', {}).get('max')
            low = price_info.get('intraDayHighLow', {}).get('min')
            close = price_info.get('close')
            volume = price_info.get('totalTradedVolume')
            c.execute('''
                INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (SYMBOL, date_str, open_, high, low, close, int(volume) if volume is not None else None))
            print(f"Inserted {SYMBOL} for {date_str}: open={open_}, high={high}, low={low}, close={close}, volume={volume}")
        except Exception as e:
            print(f"Error fetching {SYMBOL} for {date_str}: {e}")
        current += timedelta(days=1)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_and_store()
    print("Done re-fetching POWERGRID data for Jan 27, 2025 to Feb 1, 2025.")
