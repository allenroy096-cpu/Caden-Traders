import os
from dotenv import load_dotenv

# Configuration and environment variables loader
load_dotenv()

DB_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/finbot')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
NEWS_FEEDS = [
    'https://www.moneycontrol.com/rss/markets.xml',
    'https://www.livemint.com/rss/markets',
]
