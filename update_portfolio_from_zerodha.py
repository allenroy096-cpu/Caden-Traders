# Static mapping for symbol to company name (NIFTY 50 and common ETFs)
STATIC_NAME_MAP = {
	'ASHOKLEY': 'ASHOK LEYLAND',
	'GOLDBEES': 'GOLDMAN SACHS GOLD ETF',
	'HDFCBANK': 'HDFC BANK',
	'ITC': 'ITC LTD',
	'ONGC': 'OIL & NATURAL GAS CORP.',
	'RELIANCE': 'RELIANCE INDUSTRIES',
	'SBIN': 'STATE BANK OF INDIA',
	'TATAMOTORS': 'TATA MOTORS',
	'WIPRO': 'WIPRO LTD',
	# Add more as needed
}
# Static sector mapping for common Indian stocks (NIFTY 50 and popular ETFs)
STATIC_SECTOR_MAP = {
	# symbol: sector
	'ASHOKLEY': 'Automobile',
	'GOLDBEES': 'ETF',
	'HDFCBANK': 'Banking',
	'ITC': 'FMCG',
	'ONGC': 'Oil & Gas',
	'RELIANCE': 'Oil & Gas',
	'SBIN': 'Banking',
	'TATAMOTORS': 'Automobile',
	'WIPRO': 'IT',
	# name: sector (for fallback by name)
	'ASHOK LEYLAND': 'Automobile',
	'GOLDMAN SACHS GOLD ETF': 'ETF',
	'HDFC BANK': 'Banking',
	'ITC LTD': 'FMCG',
	'OIL & NATURAL GAS CORP.': 'Oil & Gas',
	'RELIANCE INDUSTRIES': 'Oil & Gas',
	'STATE BANK OF INDIA': 'Banking',
	'TATA MOTORS': 'Automobile',
	'WIPRO LTD': 'IT',
	# Add more as needed
}
import requests

# Fallback: fetch sector from Yahoo Finance public API if not found in yfinance or Zerodha
def fetch_sector_fallback(symbol):
	try:
		url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}.NS?modules=assetProfile"
		resp = requests.get(url, timeout=5)
		if resp.status_code == 200:
			data = resp.json()
			sector = data.get('quoteSummary', {}).get('result', [{}])[0].get('assetProfile', {}).get('sector')
			if sector and isinstance(sector, str):
				return sector
	except Exception:
		pass
	return 'Unknown'


from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

from models import SessionLocal, Stock, engine
import yfinance as yf


# Print DB connection string for debug
print("[DEBUG] Update script DB connection string:", engine.url)

# Load environment variables
load_dotenv()
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")

# Initialize KiteConnect after api_key and api_secret are defined
kite = KiteConnect(api_key=api_key)
import os
print("\nAfter logging in, copy the request_token from the URL and paste it below as:")
print('request_token = "PASTE_YOUR_NEW_TOKEN_HERE"')

# --- UNCOMMENT BELOW AND PASTE YOUR TOKEN TO RUN THE UPDATE ---
request_token = "Sb175dAbKLyhdVWJC2rTXi2OuXQyiurZ"  # Paste your fresh request_token here
data = kite.generate_session(request_token, api_secret=api_secret)
kite.set_access_token(data["access_token"])
holdings = kite.holdings()
print(f"Fetched {len(holdings)} holdings from Zerodha.")

session = SessionLocal()
db_symbols = {s.symbol: s for s in session.query(Stock).all()}
zerodha_symbols = set()

for h in holdings:
	symbol = h['tradingsymbol']
	zerodha_symbols.add(symbol)
	# Fetch current price and sector using yfinance
	sector = None
	try:
		ticker = yf.Ticker(symbol + ".NS")
		price = ticker.history(period="1d").iloc[-1]["Close"]
		info = ticker.info
		print(f"[DEBUG] {symbol} yfinance.info: {info}")
		sector = info.get('sector')
		if not sector or sector == 'Unknown':
			sector = info.get('industry')
	except Exception as e:
		print(f"[DEBUG] {symbol} yfinance error: {e}")
		price = None
	# Try to get sector from Zerodha holding if available
	if (not sector or sector == 'Unknown') and 'sector' in h and h['sector']:
		print(f"[DEBUG] {symbol} Zerodha sector: {h['sector']}")
		sector = h['sector']
	# Fallback: fetch sector from Yahoo Finance public API if still not found
	if not sector or sector == 'Unknown':
		fallback_sector = fetch_sector_fallback(symbol)
		print(f"[DEBUG] {symbol} fallback API sector: {fallback_sector}")
		sector = fallback_sector
	# If still unknown, try BSE ('.BO')
	if not sector or sector == 'Unknown':
		fallback_sector_bo = fetch_sector_fallback(symbol + '.BO')
		print(f"[DEBUG] {symbol} fallback API sector (BSE): {fallback_sector_bo}")
		if fallback_sector_bo and fallback_sector_bo != 'Unknown':
			sector = fallback_sector_bo
	# Final fallback: static mapping by symbol (upper), then by mapped name (upper)
	if not sector or sector == 'Unknown':
		symbol_upper = symbol.upper()
		# Try symbol in static sector map
		sector = STATIC_SECTOR_MAP.get(symbol_upper, None)
		# Try mapped name in static sector map
		stock_name_lookup = h.get('name', '').strip()
		if not stock_name_lookup or stock_name_lookup.upper() == symbol_upper:
			stock_name_lookup = STATIC_NAME_MAP.get(symbol_upper, symbol_upper)
		sector = sector or STATIC_SECTOR_MAP.get(stock_name_lookup.upper(), 'Unknown')
		print(f"[DEBUG] {symbol} static mapping sector: {sector}")
	print(f"[DEBUG] {symbol} final sector used: {sector}")
	# Use static name mapping if Zerodha name is missing or is just the symbol
	stock_name = h.get('name', '').strip()
	if not stock_name or stock_name.upper() == symbol.upper():
		stock_name = STATIC_NAME_MAP.get(symbol.upper(), symbol)
	if symbol in db_symbols:
		stock = db_symbols[symbol]
		stock.quantity = h['quantity']
		stock.buy_price = h['average_price']
		stock.name = stock_name
		stock.sector = sector or 'Unknown'
		session.add(stock)
		session.flush()  # Force DB update
		session.expire(stock)  # Expire so next access reloads from DB
		print(f"{symbol} current price (yfinance): {price}, sector: {stock.sector}, name: {stock.name}")
	else:
		stock = Stock(
			symbol=symbol,
			name=stock_name,
			quantity=h['quantity'],
			buy_price=h['average_price'],
			asset_class='Equity',
			sector=sector or 'Unknown'
		)
		session.add(stock)
		print(f"{symbol} current price (yfinance): {price}, sector: {stock.sector}, name: {stock.name}")

# Remove stocks not in Zerodha holdings
for symbol, stock in db_symbols.items():
	if symbol not in zerodha_symbols:
		session.delete(stock)

session.commit()
session.close()
print("Portfolio database updated from Zerodha holdings.")
