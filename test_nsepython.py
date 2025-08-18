import os
from kiteconnect import KiteConnect
import pandas as pd
from dotenv import load_dotenv

# Example: Fetch historical data for Power Grid Corp (POWERGRID) using Zerodha API
load_dotenv()
kite_api_key = os.getenv('KITE_API_KEY')
kite_access_token = os.getenv('KITE_ACCESS_TOKEN')
kite = KiteConnect(api_key=kite_api_key)
kite.set_access_token(kite_access_token)

symbol = 'POWERGRID'

# Get instrument token for POWERGRID
instruments = kite.instruments('NSE')
df_instruments = pd.DataFrame(instruments)
row = df_instruments[df_instruments['tradingsymbol'] == symbol]
if row.empty:
    print('POWERGRID instrument not found in Zerodha instruments list.')
else:
    instrument_token = int(row.iloc[0]['instrument_token'])
    # Fetch last 5 days of daily OHLCV
    import datetime
    end = datetime.date.today()
    start = end - datetime.timedelta(days=5)
    try:
        ohlc = kite.historical_data(
            instrument_token,
            start,
            end,
            interval='day',
            continuous=False,
            oi=False
        )
        print('Sample Zerodha OHLC data for', symbol)
        for bar in ohlc:
            print(bar)
    except Exception as e:
        print('Error fetching data from Zerodha:', e)
