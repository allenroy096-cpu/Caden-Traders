
import gzip
import pandas as pd
# --- Static sector mapping for fallback (from update_portfolio_from_zerodha.py) ---
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
STATIC_SECTOR_MAP = {
    'ASHOKLEY': 'Automobile',
    'GOLDBEES': 'ETF',
    'HDFCBANK': 'Banking',
    'ITC': 'FMCG',
    'ONGC': 'Oil & Gas',
    'RELIANCE': 'Oil & Gas',
    'SBIN': 'Banking',
    'TATAMOTORS': 'Automobile',
    'WIPRO': 'IT',
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

def get_symbol_to_sector():
    # Cache mapping in memory for performance
    if not hasattr(get_symbol_to_sector, 'cache'):
        try:
            with gzip.open('NSE.csv.gz', 'rt') as f:
                df = pd.read_csv(f)
            # Assume columns: SYMBOL, SECTOR (adjust if needed)
            mapping = dict(zip(df['SYMBOL'], df['SECTOR']))
            get_symbol_to_sector.cache = mapping
        except Exception as e:
            get_symbol_to_sector.cache = {}
    return get_symbol_to_sector.cache

from flask import jsonify, render_template, Blueprint
import sqlite3
import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

results = Blueprint('results', __name__)
DB_PATH = 'trading_bot.db'

@results.route('/api/stocks')
def api_stocks():
    load_dotenv()
    kite_api_key = os.getenv('KITE_API_KEY')
    kite_access_token = os.getenv('KITE_ACCESS_TOKEN')
    kite = KiteConnect(api_key=kite_api_key)
    kite.set_access_token(kite_access_token)
    try:
        holdings = kite.holdings()
        symbol_to_sector = get_symbol_to_sector()
        stocks = []
        for h in holdings:
            symbol = h.get('tradingsymbol')
            # Try mapping from NSE.csv.gz first
            sector = symbol_to_sector.get(symbol, None)
            # Fallback: static mapping by symbol (upper), then by mapped name (upper)
            if not sector or sector == '-' or sector == 'Unknown':
                symbol_upper = symbol.upper() if symbol else ''
                sector = STATIC_SECTOR_MAP.get(symbol_upper, None)
                # Try mapped name in static sector map
                stock_name_lookup = h.get('company_name', '').strip()
                if not stock_name_lookup or stock_name_lookup.upper() == symbol_upper:
                    stock_name_lookup = STATIC_NAME_MAP.get(symbol_upper, symbol_upper)
                sector = sector or STATIC_SECTOR_MAP.get(stock_name_lookup.upper(), 'Unknown')
            stocks.append({
                'symbol': symbol,
                'name': h.get('company_name', symbol),
                'sector': sector,
                'quantity': h.get('quantity', 0),
                'buy_price': h.get('average_price', 0),
                'current_price': h.get('last_price', 0),
                'total_investment': h.get('quantity', 0) * h.get('average_price', 0),
                'pe': h.get('pe', None),
                'dividend_yield': h.get('dividend_yield', None)
            })
        total_investment = sum(s['total_investment'] for s in stocks)
        portfolio_metrics = {'total_investment': total_investment}
        return jsonify({'stocks': stocks, 'portfolio_metrics': portfolio_metrics})
    except Exception as e:
        return jsonify({'error': str(e), 'stocks': [], 'portfolio_metrics': {}}), 500

def fetch_watchlist():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT symbol, added_on, reason FROM watchlist')
    rows = c.fetchall()
    conn.close()
    return [dict(symbol=s, added_on=a, reason=r) for s, a, r in rows]

def fetch_shortlist():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT symbol, consolidation_start, consolidation_end FROM shortlisted')
    rows = c.fetchall()
    conn.close()
    return [dict(symbol=s, consolidation_start=cs, consolidation_end=ce) for s, cs, ce in rows]

@results.route('/api/watchlist')
def api_watchlist():
    return jsonify(fetch_watchlist())

@results.route('/api/shortlist')
def api_shortlist():
    return jsonify(fetch_shortlist())

@results.route('/results')
def results_page():
    return render_template('results.html')
