import datetime
from bot.data_collection_upstox import fetch_upstox_historical

# Example: Fetch and store last 6 months of NIFTY 50 daily data
today = datetime.date.today()
six_months_ago = today - datetime.timedelta(days=180)
print("Fetching NIFTY 50 historical data from Upstox and storing in DB...")
data = fetch_upstox_historical('NIFTY 50', 'NSE_EQ', six_months_ago, today, 'day')
print(f"Fetched {len(data)} bars.")
