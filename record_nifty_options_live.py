import time
import pandas as pd
import requests
from datetime import datetime, time as dtime
import os

ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'  # Replace with your real Upstox access token
INSTRUMENT_KEY = 'NSE_INDEX|Nifty 50'
OUTPUT_FILE = 'nifty_options_live.csv'

# Market timings
START_TIME = dtime(9, 15)
END_TIME = dtime(15, 30)
INTERVAL_SECONDS = 60  # 1 minute

def fetch_option_chain():
    url = f"https://api.upstox.com/v2/option/chain?instrument_key={INSTRUMENT_KEY}"
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if 'data' in data and 'option_chain' in data['data']:
        df = pd.DataFrame(data['data']['option_chain'])
        df['timestamp'] = datetime.now()
        return df
    return None

def market_is_open():
    now = datetime.now().time()
    return START_TIME <= now <= END_TIME

print("Starting NIFTY options live data recorder...")
while True:
    if market_is_open():
        df = fetch_option_chain()
        if df is not None and not df.empty:
            write_header = not os.path.exists(OUTPUT_FILE)
            df.to_csv(OUTPUT_FILE, mode='a', header=write_header, index=False)
            print(f"Recorded {len(df)} rows at {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"No data fetched at {datetime.now().strftime('%H:%M:%S')}")
    else:
        print(f"Market closed at {datetime.now().strftime('%H:%M:%S')}. Waiting...")
    time.sleep(INTERVAL_SECONDS)
