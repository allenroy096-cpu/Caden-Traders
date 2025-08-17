from bot.data_collection import fetch_yfinance
from bot.analysis import analyze_opportunities_and_store
from bot.news_scraper import fetch_rss_entries, scrape_news_and_store

# Example: Store fetched price data as a trade
print("Fetching and storing NIFTY price...")
hist = fetch_yfinance('^NSEI')
print(hist.tail())

# Example: Store analysis results
print("Analyzing and storing opportunities...")
class Holding:
    def __init__(self, symbol):
        self.symbol = symbol
holdings = [Holding('^NSEI')]
price_data = {'^NSEI': hist}
opps = analyze_opportunities_and_store(holdings, price_data)
print(opps)

# Example: Store news from RSS feed
print("Fetching and storing news...")
entries = fetch_rss_entries('https://www.moneycontrol.com/rss/markets.xml')
news_items = [{'title': e.title, 'content': getattr(e, 'summary', ''), 'source': e.get('source', 'Moneycontrol'), 'date': getattr(e, 'published', None)} for e in entries]
scrape_news_and_store(news_items)
print(f"Stored {len(news_items)} news items.")
