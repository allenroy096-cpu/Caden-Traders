import os
from flask import Flask, render_template, request, jsonify
from models import SessionLocal, Stock, engine
print("[DEBUG] Flask app DB connection string:", engine.url)

import random
import yfinance as yf
import pandas as pd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)


# Ensure all tables are created at startup
try:
    from bot.config.models import init_db
    init_db()
except Exception as e:
    print(f"[DB INIT ERROR] {e}")



# --- SINGLE FLASK APP INSTANCE AT TOP ---



# --- Darvas Box Strategy: Fetch NIFTY 50 stocks and historical prices from yfinance ---
@app.route('/api/darvas_test')
def api_darvas_box_test():
    # NIFTY 50 symbols (NSE)
    nifty50_symbols = [
        'ADANIPORTS', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL',
        'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT',
        'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR',
        'ICICIBANK', 'INDUSINDBK', 'INFY', 'ITC', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI',
        'NESTLEIND', 'NTPC', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SHREECEM',
        'SUNPHARMA', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TCS', 'TECHM', 'TITAN', 'ULTRACEMCO',
        'UPL', 'WIPRO'
    ]
    # Add .NS for yfinance
    symbols = [s + '.NS' for s in nifty50_symbols]
    # Randomly select 50
    selected = random.sample(symbols, min(50, len(symbols)))
    results = []
    total = len(selected)
    for idx, symbol in enumerate(selected, 1):
        try:
            print(f"[Darvas] Fetching {symbol} ({idx}/{total})...")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2mo')
            close_prices = hist['Close'].dropna().tolist()
            if len(close_prices) < 30:
                print(f"[Darvas] {symbol}: Not enough data, skipping.")
                continue
            box_high = max(close_prices[-30:])
            box_low = min(close_prices[-30:])
            last_price = close_prices[-1]
            action = 'HOLD'
            if last_price > box_high:
                action = 'BUY'
            elif last_price < box_low:
                action = 'SELL'
            results.append({
                'symbol': symbol,
                'box_high': box_high,
                'box_low': box_low,
                'last_price': last_price,
                'action': action
            })
            print(f"[Darvas] {symbol}: Done.")
        except Exception as e:
            print(f"[Darvas] {symbol}: Error {e}")
# --- ML Learning from Strategy Test Data ---


@app.route('/api/learn', methods=['POST'])
def api_learn_from_strategy():
    session = SessionLocal()
    results = session.query(AnalysisResult).all()
    session.close()
    # Parse results into DataFrame
    records = []
    for r in results:
        try:
            d = eval(r.result) if r.result.strip().startswith('{') else {'action': r.result}
            d['symbol'] = r.symbol
            d['created_at'] = r.created_at
            records.append(d)
        except Exception:
            continue
    if not records:
        return jsonify({'error': 'No strategy results to learn from.'}), 400
    df = pd.DataFrame(records)
    # Example: Calculate win ratio, mean reward, action counts
    summary = {}
    if 'action' in df.columns and 'price' in df.columns:
        action_counts = df['action'].value_counts().to_dict()
        summary['action_counts'] = action_counts
        # If you have outcome/reward columns, add more ML logic here
        # For now, just print summary
    print('ML Learning Summary:', summary)
    return jsonify({'summary': summary, 'count': len(df)})



from flask import Flask, render_template, request, jsonify
import time
import yfinance as yf
# --- Update stocks with live prices using yfinance ---
def update_stocks_with_live_prices():
    from models import SessionLocal, Stock
    session = SessionLocal()
    errors = []
    for stock in session.query(Stock).all():
        try:
            ticker = yf.Ticker(stock.symbol + ".NS")
            price = None
            if hasattr(ticker, 'fast_info') and 'last_price' in ticker.fast_info:
                price = ticker.fast_info['last_price']
            if price is None:
                price = ticker.info.get('regularMarketPrice')
            if price is not None:
                stock.current_price = price
            else:
                errors.append(stock.symbol)
        except Exception as e:
            errors.append(stock.symbol)
    session.commit()
    session.close()
    return errors







import sys
print("[DEBUG] Python executable:", sys.executable)
print("[DEBUG] sys.path:", sys.path)

from flask import Flask, render_template, request, jsonify
from bot.config.models import SessionLocal, AnalysisResult


# --- SINGLE FLASK APP INSTANCE AT TOP ---


# --- API ROUTES ---


@app.route('/api/strategy_signals')
def api_strategy_signals():
    session = SessionLocal()
    signals = session.query(AnalysisResult).filter(AnalysisResult.result.contains('action')).order_by(AnalysisResult.created_at.desc()).limit(20).all()
    strategy_signals = [
        {
            'symbol': s.symbol,
            'result': s.result,
            'created_at': s.created_at.strftime('%Y-%m-%d') if s.created_at else ''
        } for s in signals
    ]
    session.close()
    return jsonify({'strategy_signals': strategy_signals})





# Fetch live price from Upstox API



# --- Simple in-memory cache for yfinance results ---
yf_cache = {}
YF_CACHE_TTL = 300  # seconds (5 minutes)


def fetch_yfinance_live_price(symbol):
    now = time.time()
    cache_key = f"price_{symbol}"
    if cache_key in yf_cache and now - yf_cache[cache_key]['ts'] < YF_CACHE_TTL:
        return yf_cache[cache_key]['price']
        try:
            ticker = yf.Ticker(symbol + ".NS")
            price = ticker.fast_info['last_price'] if 'last_price' in ticker.fast_info else None
            if price is None:
                price = ticker.info.get('regularMarketPrice')
            yf_cache[cache_key] = {'price': price, 'ts': now}
            return price
        except Exception as e:
            import logging
            logging.error(f"yfinance error for {symbol}: {e}")
            return None



# Calculate Sector and Asset Weightage using DB
from models import SessionLocal, Stock
session = SessionLocal()
stocks_db = session.query(Stock).all()
sector_totals = {}
for stock in stocks_db:
    sector = stock.sector
    if sector not in sector_totals:
        sector_totals[sector] = sum(s.buy_price * s.quantity for s in stocks_db if s.sector == sector)
portfolio_total = sum(s.buy_price * s.quantity for s in stocks_db)
for stock in stocks_db:
    stock.sector_weightage = sector_totals[stock.sector]
    stock.sector_weightage_pct = (sector_totals[stock.sector] / portfolio_total * 100) if portfolio_total else 0

asset_totals = {}
for stock in stocks_db:
    asset = stock.asset_class
    asset_totals[asset] = asset_totals.get(asset, 0) + (stock.buy_price * stock.quantity)
for stock in stocks_db:
    stock.asset_weightage = asset_totals[stock.asset_class]
    stock.asset_weightage_pct = (asset_totals[stock.asset_class] / portfolio_total * 100) if portfolio_total else 0
session.commit()
session.close()


# --- Portfolio Analytics: Risk, Performance, Forecast, Economic Metrics ---
import numpy as np
import datetime

# Simulate historical prices for demo (replace with real data for production)
def simulate_historical_prices(stock, days=90):
    np.random.seed(hash(stock['symbol']) % 2**32)
    base = stock['buy_price']
    returns = np.random.normal(0.0005, 0.02, days)  # mean daily return, stddev
    prices = [base]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    return prices[1:]


# Calculate metrics for each stock from DB
import numpy as np
from models import SessionLocal, Stock
session = SessionLocal()
stocks_db = session.query(Stock).all()
def simulate_historical_prices(stock, days=90):
    np.random.seed(hash(stock.symbol) % 2**32)
    base = stock.buy_price
    returns = np.random.normal(0.0005, 0.02, days)
    prices = [base]
    for r in returns:
        prices.append(prices[-1] * (1 + r))
    return prices[1:]
for stock in stocks_db:
    hist_prices = simulate_historical_prices(stock)
    stock.hist_prices = list(hist_prices)
    daily_returns = np.diff(hist_prices) / hist_prices[:-1]
    stock.daily_returns = list(daily_returns)
    stock.volatility = float(np.std(daily_returns)) if len(daily_returns) > 0 else 0
    stock.avg_return = float(np.mean(daily_returns)) if len(daily_returns) > 0 else 0
    stock.sharpe = (stock.avg_return / stock.volatility) if stock.volatility else 0
    stock.max_drawdown = float(np.min(hist_prices) / np.max(hist_prices) - 1) if len(hist_prices) > 1 else 0
session.commit()
daily_returns_arrays = [np.array(stock.daily_returns) for stock in stocks_db if hasattr(stock, 'daily_returns') and len(stock.daily_returns) > 0]
if daily_returns_arrays:
    all_returns = np.concatenate(daily_returns_arrays)
else:
    all_returns = np.array([])
portfolio_volatility = float(np.std(all_returns)) if len(all_returns) > 0 else 0
portfolio_avg_return = float(np.mean(all_returns)) if len(all_returns) > 0 else 0
portfolio_sharpe = (portfolio_avg_return / portfolio_volatility) if portfolio_volatility else 0
portfolio_max_drawdown = float(np.min([np.min(stock.hist_prices) / np.max(stock.hist_prices) - 1 for stock in stocks_db if hasattr(stock, 'hist_prices') and len(stock.hist_prices) > 1])) if stocks_db else 0
session.close()

# Economic indicators (dummy data for demo)
economic_metrics = {
    'nifty_index': 22000,
    'nifty_change_pct': 0.45,
    'inflation': 5.2,
    'interest_rate': 6.5,
    'gdp_growth': 7.1,
    'sector_indices': {
        'Banking': 48000,
        'IT': 32000,
        'Automobile': 18000,
        'Pharmaceuticals': 15000,
        'FMCG': 14000,
        'Oil & Gas': 12000,
        'Conglomerate': 10000,
        'Unknown': 5000
    }
}


# --- Opportunity & Threat Detection (Basic Demo) ---
def detect_opportunities_and_threats(stocks):
    insights = []
    for stock in stocks:
        # Example: Opportunity if price is near 52-week low, threat if near 52-week high
        # (In real use, fetch 52-week data from yfinance)
        try:
            ticker = yf.Ticker(stock['symbol'] + ".NS")
            hist = ticker.history(period="1y")
            if not hist.empty:
                low_52w = hist['Low'].min()
                high_52w = hist['High'].max()
                last_price = stock.get('current_price', stock['buy_price'])
                if last_price <= low_52w * 1.05:
                    insights.append({
                        'type': 'opportunity',
                        'symbol': stock['symbol'],
                        'message': f"{stock['name']} is near its 52-week low (₹{low_52w:.2f}). Consider for accumulation."
                    })
                elif last_price >= high_52w * 0.98:
                    insights.append({
                        'type': 'threat',
                        'symbol': stock['symbol'],
                        'message': f"{stock['name']} is near its 52-week high (₹{high_52w:.2f}). Watch for profit booking or reversal."
                    })
        except Exception as e:
            continue
    return insights





# --- API: Insights (JSON) ---


# API: Portfolio stocks and metrics
@app.route('/api/stocks')
def api_stocks():
    # Restore live price fetching, but add timeout and error handling
    session = SessionLocal()
    stocks_db = session.query(Stock).all()
    # Convert to dicts for JSON response and calculations
    stocks = []
    import yfinance as yf
    # Static mappings (should match those in update_portfolio_from_zerodha.py)
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
    }
    def get_live_name_and_sector(symbol):
        # Try yfinance first
        try:
            ticker = yf.Ticker(symbol + ".NS")
            info = ticker.info
            name = info.get('longName') or info.get('shortName') or STATIC_NAME_MAP.get(symbol.upper(), symbol)
            sector = info.get('sector') or info.get('industry')
        except Exception:
            name = STATIC_NAME_MAP.get(symbol.upper(), symbol)
            sector = None
        # Fallback to static mapping if needed
        if not name or name.upper() == symbol.upper():
            name = STATIC_NAME_MAP.get(symbol.upper(), symbol)
        sector_lookup = name.strip().upper() if name else symbol.upper()
        if not sector or sector == 'Unknown':
            sector = STATIC_SECTOR_MAP.get(symbol.upper(), None)
            sector = sector or STATIC_SECTOR_MAP.get(sector_lookup, 'Unknown')
        return name, sector

    for s in stocks_db:
        try:
            ticker = yf.Ticker(s.symbol + ".NS")
            ltp = None
            # Try fast_info first (fastest and most reliable for LTP)
            if hasattr(ticker, 'fast_info') and 'last_price' in ticker.fast_info:
                ltp = ticker.fast_info['last_price']
            if ltp is None:
                ltp = ticker.info.get('regularMarketPrice')
        except Exception:
            ltp = None
        name, sector = get_live_name_and_sector(s.symbol)
        stock_dict = {
            'id': s.id,
            'name': name,
            'symbol': s.symbol,
            'asset_class': s.asset_class,
            'sector': sector,
            'buy_price': s.buy_price,
            'quantity': s.quantity,
            'total_investment': (s.buy_price or 0) * (s.quantity or 0),
            'current_price': ltp,
        }
        stocks.append(stock_dict)
    portfolio_total = sum(stock['total_investment'] for stock in stocks)
    # If you want to update live prices, you can do it here (optional)
    errors = []
    session.close()
    # Example portfolio metrics (replace with your real calculations as needed)
    portfolio_metrics = {
        'total_investment': portfolio_total,
        # Add more metrics as needed
    }
    response = {
        'stocks': stocks,
        'portfolio_metrics': portfolio_metrics,
        # 'economic_metrics': economic_metrics,  # Remove or update as needed
    }
    if len(errors) == len(stocks):
        response['warning'] = 'Failed to fetch live prices for all stocks. Using buy prices as fallback.'
    elif errors:
        response['warning'] = f"Failed to fetch prices for: {', '.join(errors)}. Using buy prices as fallback."
    return jsonify(response)


# Quant Trading: Moving Average Crossover Backtest
def moving_average_crossover_backtest(symbol, short_window=20, long_window=50):
    import pandas as pd
    now = time.time()
    cache_key = f"hist_{symbol}"
    if cache_key in yf_cache and now - yf_cache[cache_key]['ts'] < YF_CACHE_TTL:
        hist = yf_cache[cache_key]['hist']
    else:
        try:
            ticker = yf.Ticker(symbol + ".NS")
            hist = ticker.history(period="1y")
            yf_cache[cache_key] = {'hist': hist, 'ts': now}
        except Exception as e:
            return {'error': str(e)}
    try:
        if hist.empty:
            return {'error': 'No data'}
        hist['SMA_short'] = hist['Close'].rolling(window=short_window).mean()
        hist['SMA_long'] = hist['Close'].rolling(window=long_window).mean()
        hist['signal'] = 0
        hist.loc[hist['SMA_short'] > hist['SMA_long'], 'signal'] = 1
        hist.loc[hist['SMA_short'] < hist['SMA_long'], 'signal'] = -1
        hist['position'] = hist['signal'].shift(1).fillna(0)
        hist['returns'] = hist['Close'].pct_change().fillna(0)
        hist['strategy_returns'] = hist['returns'] * hist['position']
        total_return = (hist['strategy_returns'] + 1).prod() - 1
        trades = hist[hist['signal'].diff() != 0][['Close', 'signal']]
        return {
            'symbol': symbol,
            'total_return': float(total_return),
            'trades': trades.reset_index().to_dict(orient='records'),
            'history': hist[['Close', 'SMA_short', 'SMA_long', 'position', 'strategy_returns']].reset_index().to_dict(orient='records')
        }
    except Exception as e:
        return {'error': str(e)}







# --- SINGLE FLASK APP INSTANCE AT TOP ---


# --- Dynamic Instrument Test Page ---




# --- MAIN ROUTES ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/portfolio')
def portfolio_page():
    print("[DEBUG] /portfolio route called")
    result = render_template('portfolio.html')
    print("[DEBUG] render_template executed, returning response")
    return result


# --- STRATEGY TEST PAGE ROUTE ---
@app.route('/strategy_test')
def strategy_test():
    try:
        api_learn_from_strategy()
    except Exception as e:
        print(f"ML learning error: {e}")
    return render_template('strategy_test.html')

# --- Portfolio Insights API: Advanced Metrics & Analytics ---
import numpy as np
@app.route('/api/portfolio_insights')
def api_portfolio_insights():
    import yfinance as yf
    # Use the same static mappings as in /api/stocks
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
    }
    def get_live_name_and_sector(symbol):
        try:
            ticker = yf.Ticker(symbol + ".NS")
            info = ticker.info
            name = info.get('longName') or info.get('shortName') or STATIC_NAME_MAP.get(symbol.upper(), symbol)
            sector = info.get('sector') or info.get('industry')
        except Exception:
            name = STATIC_NAME_MAP.get(symbol.upper(), symbol)
            sector = None
        if not name or name.upper() == symbol.upper():
            name = STATIC_NAME_MAP.get(symbol.upper(), symbol)
        sector_lookup = name.strip().upper() if name else symbol.upper()
        if not sector or sector == 'Unknown':
            sector = STATIC_SECTOR_MAP.get(symbol.upper(), None)
            sector = sector or STATIC_SECTOR_MAP.get(sector_lookup, 'Unknown')
        return name, sector

    session = SessionLocal()
    stocks_db = session.query(Stock).all()
    session.close()
    # Fetch live prices and build portfolio
    portfolio = []
    for s in stocks_db:
        try:
            ticker = yf.Ticker(s.symbol + ".NS")
            ltp = None
            hist = ticker.history(period='6mo', interval='1d')
            if hasattr(ticker, 'fast_info') and 'last_price' in ticker.fast_info:
                ltp = ticker.fast_info['last_price']
            if ltp is None:
                ltp = ticker.info.get('regularMarketPrice')
        except Exception:
            ltp = None
            hist = None
        name, sector = get_live_name_and_sector(s.symbol)
        portfolio.append({
            'symbol': s.symbol,
            'name': name,
            'sector': sector,
            'quantity': s.quantity,
            'buy_price': s.buy_price,
            'current_price': ltp,
            'hist': hist['Close'].tolist() if hist is not None and not hist.empty else [],
        })
    # Metrics
    invested = sum(p['buy_price'] * p['quantity'] for p in portfolio)
    present_value = sum((p['current_price'] or 0) * p['quantity'] for p in portfolio)
    pl = present_value - invested
    pl_pct = (pl / invested * 100) if invested else 0
    # Advanced metrics
    all_hist = []
    for p in portfolio:
        if p['hist']:
            all_hist.append(np.array(p['hist']))
    # Portfolio returns (simple, not time-weighted)
    returns = []
    for p in portfolio:
        if len(p['hist']) > 1:
            arr = np.array(p['hist'])
            ret = np.diff(arr) / arr[:-1]
            returns.extend(ret)
    volatility = float(np.std(returns)) if returns else 0
    avg_return = float(np.mean(returns)) if returns else 0
    sharpe = (avg_return / volatility) if volatility else 0
    # Value at Risk (VaR) 95%
    var_95 = float(np.percentile(returns, 5)) if returns else 0
    # Max drawdown
    max_drawdown = 0
    if all_hist:
        all_hist_concat = np.concatenate(all_hist)
        roll_max = np.maximum.accumulate(all_hist_concat)
        drawdowns = (all_hist_concat - roll_max) / roll_max
        max_drawdown = float(drawdowns.min()) if len(drawdowns) > 0 else 0
    # Sector allocation
    sector_alloc = {}
    for p in portfolio:
        if p['sector'] not in sector_alloc:
            sector_alloc[p['sector']] = 0
        sector_alloc[p['sector']] += (p['current_price'] or 0) * p['quantity']
    # Insights
    insights = []
    if pl < 0:
        insights.append('Your portfolio is at a loss. Review your holdings.')
    if volatility > 0.03:
        insights.append('High volatility detected. Consider diversifying.')
    if max_drawdown < -0.2:
        insights.append('Significant drawdown observed. Review risk management.')
    if sharpe < 0.5:
        insights.append('Low Sharpe ratio. Portfolio risk-adjusted returns are low.')
    # Top gainers/losers
    perf = [(p['symbol'], ((p['current_price'] or 0) - p['buy_price']) / p['buy_price'] * 100 if p['buy_price'] else 0) for p in portfolio]
    perf_sorted = sorted(perf, key=lambda x: x[1], reverse=True)
    top_gainers = perf_sorted[:3]
    top_losers = perf_sorted[-3:]
    # Response
    return jsonify({
        'metrics': {
            'invested': invested,
            'present_value': present_value,
            'pl': pl,
            'pl_pct': pl_pct,
            'volatility': volatility,
            'avg_return': avg_return,
            'sharpe': sharpe,
            'var_95': var_95,
            'max_drawdown': max_drawdown,
        },
        'sector_allocation': sector_alloc,
        'insights': insights,
        'top_gainers': top_gainers,
        'top_losers': top_losers,
        'chart_data': {
            'history': [p['hist'] for p in portfolio if p['hist']],
            'symbols': [p['symbol'] for p in portfolio if p['hist']],
        }
    })

if __name__ == "__main__":
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True, port=5050)
