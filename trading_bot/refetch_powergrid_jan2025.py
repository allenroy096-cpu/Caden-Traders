## Removed unused nsepython import
import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'trading_bot.db'
SYMBOL = 'POWERGRID.NS'
NSE_SYMBOL = 'POWERGRID'

# Dates for the week of Jan 27, 2025 to Feb 1, 2025
start_date = datetime(2025, 1, 27)
end_date = datetime(2025, 2, 1)

def fetch_and_store():
    from kiteconnect import KiteConnect
    import os
    import time
    import pandas as pd
    from dotenv import load_dotenv

    load_dotenv()
    kite_api_key = os.getenv('KITE_API_KEY')
    kite_access_token = os.getenv('KITE_ACCESS_TOKEN')
    kite = KiteConnect(api_key=kite_api_key)
    kite.set_access_token(kite_access_token)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Zerodha expects instrument_token, not symbol
    # We'll fetch instrument_token for POWERGRID.NS
    instruments = kite.instruments('NSE')
    df_instruments = pd.DataFrame(instruments)
    row = df_instruments[df_instruments['tradingsymbol'] == 'POWERGRID']
    if row.empty:
        print('POWERGRID instrument not found in Zerodha instruments list.')
        return
    instrument_token = int(row.iloc[0]['instrument_token'])

    # Fetch daily OHLCV for the date range
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        try:
            ohlc = kite.historical_data(
                instrument_token,
                current,
                current,
                interval='day',
                continuous=False,
                oi=False
            )
            if ohlc:
                bar = ohlc[0]
                open_ = bar['open']
                high = bar['high']
                low = bar['low']
                close = bar['close']
                volume = bar['volume']
                c.execute('''
                    INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (SYMBOL, date_str, open_, high, low, close, int(volume) if volume is not None else None))
                print(f"Inserted {SYMBOL} for {date_str}: open={open_}, high={high}, low={low}, close={close}, volume={volume}")
            else:
                print(f"No data for {SYMBOL} on {date_str}")
        except Exception as e:
            print(f"Error fetching {SYMBOL} for {date_str}: {e}")
        time.sleep(0.5)  # avoid rate limits
        current += timedelta(days=1)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fetch_and_store()
    print("Done re-fetching POWERGRID data for Jan 27, 2025 to Feb 1, 2025.")
