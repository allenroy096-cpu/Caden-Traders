try:
    from .config.models import SessionLocal, News  # type: ignore[import]
except ImportError:
    from bot.config.models import SessionLocal, News  # type: ignore[import]

def scrape_news_and_store(news_items):
    session = SessionLocal()
    try:
        for item in news_items:
            news = News(
                headline=item.get('title', 'No Title'),
                content=item.get('content', ''),
                source=item.get('source', 'Unknown'),
                published_at=item.get('date')
            )
            session.add(news)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"DB Error: {e}")
    finally:
        session.close()
import feedparser
import requests
from bs4 import BeautifulSoup
import hashlib

# Fetch and parse RSS feed entries
def fetch_rss_entries(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        return feed.entries
    except Exception as e:
        print(f"RSS error: {e}")
        return []

# Scrape news articles from a web page (generic)
def scrape_news_page(url, article_selector, title_selector, date_selector=None):
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        articles = []
        for article in soup.select(article_selector):
            title = article.select_one(title_selector).get_text(strip=True) if article.select_one(title_selector) else None
            date = article.select_one(date_selector).get_text(strip=True) if date_selector and article.select_one(date_selector) else None
            link = article.find('a')['href'] if article.find('a') else None
            if title and link:
                articles.append({'title': title, 'date': date, 'link': link})
        return articles
    except Exception as e:
        print(f"Scrape error: {e}")
        return []

# Deduplicate news by title hash
def deduplicate_news(news_list):
    seen = set()
    deduped = []
    for item in news_list:
        h = hashlib.sha256(item['title'].encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            deduped.append(item)
    return deduped

# Example usage:
# entries = fetch_rss_entries('https://www.moneycontrol.com/rss/markets.xml')
# news = scrape_news_page('https://www.moneycontrol.com/news/business/markets/', 'li.clearfix', 'h2')
# news = deduplicate_news(news)
