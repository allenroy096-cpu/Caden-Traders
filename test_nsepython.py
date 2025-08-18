from nsepython import nsefetch
import pandas as pd

# Example: Fetch historical data for Power Grid Corp (POWERGRID)
# NSE symbol format: 'POWERGRID'
# NSE API endpoint for historical data (public, but may change)
# This is a demonstration; for production, use official NSE Bhavcopy or paid APIs for reliability

symbol = 'POWERGRID'
url = f'https://www.nseindia.com/api/quote-equity?symbol={symbol}'

try:
    data = nsefetch(url)
    print('Sample NSE data for', symbol)
    print(data)
except Exception as e:
    print('Error fetching data from NSE:', e)
