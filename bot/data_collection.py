
import yfinance as yf
# Try both relative and absolute imports for models, and ignore linter warnings if unresolved
try:
    from .config.models import SessionLocal, Trade  # type: ignore[import]
except ImportError:
    from bot.config.models import SessionLocal, Trade  # type: ignore[import]
import requests
import pandas as pd
import os

# Example: Fetch stock data from yfinance
def fetch_yfinance(symbol, period='1y', interval='1d'):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        # Example: store a trade in the database (for demonstration)
        session = SessionLocal()
        try:
            if not hist.empty:
                last_close = hist['Close'].iloc[-1]
                trade = Trade(symbol=symbol, trade_type='FETCH', quantity=0, price=float(last_close))
                session.add(trade)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"DB Error: {e}")
        finally:
            session.close()
        return hist
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")
        return None

# Example: Fetch stock data from Alpha Vantage (requires API key)
def fetch_alpha_vantage(symbol, api_key=None):
    api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data
    except Exception as e:
        print(f"Alpha Vantage error for {symbol}: {e}")
        return None

# Example: Fetch stock data from Finnhub (requires API key)
def fetch_finnhub(symbol, api_key=None):
    api_key = api_key or os.getenv('FINNHUB_API_KEY')
    url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
    try:
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"Finnhub error for {symbol}: {e}")
        return None

# Example: Fetch BSE/NSE data (placeholder, as scraping may be required)
def fetch_nse(symbol):
    # NSE India blocks most direct requests; use nsetools or web scraping as needed
    try:
        # Placeholder: return None or implement with nsetools
        return None
    except Exception as e:
        print(f"NSE error for {symbol}: {e}")
        return None

# Example: Fetch news from RSS feeds
def fetch_rss_feed(url):
    import feedparser
    try:
        feed = feedparser.parse(url)
        return feed.entries
    except Exception as e:
        print(f"RSS feed error: {e}")
        return []

# Add more data sources as needed
