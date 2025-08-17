import pandas as pd
from datetime import datetime, timedelta

# Parameters for synthetic NIFTY options
start_date = datetime(2024, 4, 1)
end_date = datetime(2025, 3, 31)
expiries = pd.date_range(start_date, end_date, freq='W-THU')  # Weekly expiry (Thursday)
strikes = list(range(18000, 25001, 100))  # 18000 to 25000, step 100
option_types = ['CE', 'PE']

rows = []
token = 1000000
for expiry in expiries:
    for strike in strikes:
        for opt_type in option_types:
            rows.append({
                'underlying': 'NIFTY',
                'expiry': expiry.strftime('%Y-%m-%d'),
                'strike_price': strike,
                'option_type': opt_type,
                'instrument_token': token
            })
            token += 1

df = pd.DataFrame(rows)
df.to_csv('NSE_FO.csv', index=False)
print(f"Generated NSE_FO.csv with {len(df)} rows.")
