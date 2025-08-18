import requests
import pandas as pd
from db import get_connection

def fetch_news_sentiment(symbol):
    # Example: Use Yahoo Finance news headlines (free, but limited)
    url = f'https://query1.finance.yahoo.com/v1/finance/search?q={symbol}'
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        headlines = [item['title'] for item in data.get('news', [])]
        # Simple sentiment: +1 for positive, -1 for negative, 0 for neutral (placeholder logic)
        pos_words = ['gain', 'rise', 'up', 'profit', 'beat']
        neg_words = ['fall', 'down', 'loss', 'miss', 'drop']
        score = 0
        for h in headlines:
            h_lower = h.lower()
            if any(w in h_lower for w in pos_words):
                score += 1
            if any(w in h_lower for w in neg_words):
                score -= 1
        return score / max(1, len(headlines)) if headlines else 0
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return 0

def update_news_sentiment():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT symbol FROM stock_prices')
        symbols = [row[0] for row in c.fetchall()]
        results = []
        for symbol in symbols:
            score = fetch_news_sentiment(symbol)
            results.append({'symbol': symbol, 'sentiment': score})
        df = pd.DataFrame(results)
        df.to_csv('news_sentiment.csv', index=False)
        print('News sentiment exported to news_sentiment.csv')

if __name__ == "__main__":
    update_news_sentiment()
