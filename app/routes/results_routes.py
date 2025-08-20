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
    'LIQUIDBEES': 'Debt',  # Added mapping for Liquid Bees
    'ASHOK LEYLAND': 'Automobile',
    'GOLDMAN SACHS GOLD ETF': 'ETF',
    'HDFC BANK': 'Banking',
    'ITC LTD': 'FMCG',
    'OIL & NATURAL GAS CORP.': 'Oil & Gas',
    'RELIANCE INDUSTRIES': 'Oil & Gas',
    'STATE BANK OF INDIA': 'Banking',
    'TATA MOTORS': 'Automobile',
    'WIPRO LTD': 'IT',
    'NIPPON INDIA ETF LIQUID BEES': 'Debt',  # Common name for Liquid Bees
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
from models import SessionLocal, Stock

results = Blueprint('results', __name__)
DB_PATH = 'trading_bot.db'

@results.route('/api/stocks')
def api_stocks():
    import numpy as np
    load_dotenv()
    kite_api_key = os.getenv('KITE_API_KEY')
    kite_access_token = os.getenv('KITE_ACCESS_TOKEN')
    kite = KiteConnect(api_key=kite_api_key)
    kite.set_access_token(kite_access_token)
    try:
        holdings = kite.holdings()
        symbol_to_sector = get_symbol_to_sector()
        stocks = []
        returns = []
        total_investment = 0
        present_value = 0
        for h in holdings:
            symbol = h.get('tradingsymbol')
            sector = symbol_to_sector.get(symbol, None)
            if not sector or sector == '-' or sector == 'Unknown':
                symbol_upper = symbol.upper() if symbol else ''
                sector = STATIC_SECTOR_MAP.get(symbol_upper, None)
                stock_name_lookup = h.get('company_name', '').strip()
                if not stock_name_lookup or stock_name_lookup.upper() == symbol_upper:
                    stock_name_lookup = STATIC_NAME_MAP.get(symbol_upper, symbol_upper)
                sector = sector or STATIC_SECTOR_MAP.get(stock_name_lookup.upper(), 'Unknown')
            qty = h.get('quantity', 0)
            buy_price = h.get('average_price', 0)
            curr_price = h.get('last_price', 0)
            invested_amt = qty * buy_price
            curr_val = qty * curr_price
            total_investment += invested_amt
            present_value += curr_val
            avg_return = ((curr_price - buy_price) / buy_price) if buy_price else 0
            returns.append(avg_return)
            stocks.append({
                'symbol': symbol,
                'name': h.get('company_name', symbol),
                'sector': sector,
                'quantity': qty,
                'buy_price': buy_price,
                'current_price': curr_price,
                'total_investment': invested_amt,
                'pe': h.get('pe', None),
                'dividend_yield': h.get('dividend_yield', None),
                'avg_return': avg_return
            })
        # Portfolio metrics
        pl = present_value - total_investment
        pl_pct = (pl / total_investment * 100) if total_investment else 0
        volatility = float(np.std(returns)) if returns else 0
        avg_return = float(np.mean(returns)) if returns else 0
        risk_free = 0.06 / 252
        sharpe = ((avg_return - risk_free) / (volatility + 1e-8)) if volatility else 0
        # Max drawdown (worst drop from peak)
        def max_drawdown(returns):
            arr = np.array(returns)
            if arr.size == 0:
                return 0
            peak = arr[0]
            max_dd = 0
            for x in arr:
                if x > peak:
                    peak = x
                dd = (peak - x) / (peak if peak != 0 else 1)
                if dd > max_dd:
                    max_dd = dd
            return max_dd
        max_dd = max_drawdown(returns)
        portfolio_metrics = {
            'volatility': volatility,
            'avg_return': avg_return,
            'sharpe': sharpe,
            'max_drawdown': max_dd,
            'total_investment': total_investment,
            'pl': pl,
            'pl_pct': pl_pct
        }
        # Economic metrics (static or mock for now)
        economic_metrics = {
            'nifty_index': 22000,
            'nifty_change_pct': 0.012,
            'inflation': 5.2,
            'interest_rate': 6.5,
            'gdp_growth': 6.8
        }
        return jsonify({'stocks': stocks, 'portfolio_metrics': portfolio_metrics, 'economic_metrics': economic_metrics})
    except Exception as e:
        print("[ERROR in /api/stocks]", e, flush=True)
        return jsonify({'error': str(e), 'stocks': [], 'portfolio_metrics': {}, 'economic_metrics': {}}), 500

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

@results.route('/api/portfolio_insights')
def api_portfolio_insights():
    # Full analytics for advanced insights tab
    from models import SessionLocal, Stock
    import numpy as np
    session = SessionLocal()
    try:
        db_stocks = session.query(Stock).all()
        if not db_stocks:
            return jsonify({'error': 'No portfolio data found.'}), 404
        # Prepare lists for analytics
        invested = 0
        present_value = 0
        returns = []
        sector_alloc = {}
        stock_gains = []
        stock_losses = []
        for s in db_stocks:
            qty = s.quantity or 0
            buy = s.buy_price or 0
            # Try to get current price from Stock if available, else fallback to buy price
            curr = getattr(s, 'current_price', None)
            if curr is None:
                curr = buy
            invested_amt = qty * buy
            curr_val = qty * curr
            invested += invested_amt
            present_value += curr_val
            if invested_amt > 0:
                ret = (curr_val - invested_amt) / invested_amt
                returns.append(ret)
                if ret >= 0:
                    stock_gains.append((s.symbol, ret * 100))
                else:
                    stock_losses.append((s.symbol, ret * 100))
            sector = s.sector or 'Unknown'
            sector_alloc[sector] = sector_alloc.get(sector, 0) + invested_amt
        pl = present_value - invested
        pl_pct = (pl / invested * 100) if invested else 0
        # Volatility (stddev of returns)
        volatility = float(np.std(returns)) if returns else 0
        # Sharpe ratio (assume risk-free rate 6%)
        risk_free = 0.06 / 252  # daily
        mean_ret = float(np.mean(returns)) if returns else 0
        sharpe = ((mean_ret - risk_free) / (volatility + 1e-8)) if volatility else 0
        # VaR 95% (Value at Risk)
        var_95 = float(np.percentile(returns, 5)) if returns else 0
        # Max drawdown (worst drop from peak)
        def max_drawdown(returns):
            arr = np.array(returns)
            if arr.size == 0:
                return 0
            peak = arr[0]
            max_dd = 0
            for x in arr:
                if x > peak:
                    peak = x
                dd = (peak - x) / (peak if peak != 0 else 1)
                if dd > max_dd:
                    max_dd = dd
            return max_dd
        max_dd = max_drawdown(returns)
        # Insights
        insights = []
        if pl < 0:
            insights.append("Portfolio is currently at a loss.")
        if volatility > 0.03:
            insights.append("High volatility detected in portfolio returns.")
        if max_dd > 0.2:
            insights.append("Significant drawdown observed in portfolio.")
        if sharpe < 1:
            insights.append("Low Sharpe ratio: risk-adjusted returns could be improved.")
        # Top gainers/losers
        top_gainers = sorted(stock_gains, key=lambda x: -x[1])[:3]
        top_losers = sorted(stock_losses, key=lambda x: x[1])[:3]
        # Sector allocation (absolute values)
        sector_allocation = {k: float(v) for k, v in sector_alloc.items()}
        # Metrics summary
        metrics = {
            'invested': float(invested),
            'present_value': float(present_value),
            'pl': float(pl),
            'pl_pct': float(pl_pct),
            'volatility': float(volatility),
            'sharpe': float(sharpe),
            'var_95': float(var_95),
            'max_drawdown': float(max_dd),
        }
        return jsonify({
            'metrics': metrics,
            'sector_allocation': sector_allocation,
            'insights': insights,
            'top_gainers': top_gainers,
            'top_losers': top_losers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
