# Self-Learning Financial Analysis Bot

A modular Python project that:
1. Collects financial data and news from open sources (yfinance, Alpha Vantage, Finnhub, EDGAR, BSE/NSE, RSS feeds)
2. Stores data in a database
3. Parses and summarizes financial reports
4. Analyzes for trade opportunities and risks
5. Integrates with a portfolio
6. Logs decisions and outcomes for self-improvement
7. Automates updates and sends alerts

## Structure
- bot/
  - __init__.py
  - data_collection.py
  - news_scraper.py
  - report_parser.py
  - analysis.py
  - portfolio.py
  - learning.py
  - scheduler.py
  - alerts.py
  - config.py
- requirements.txt
- README.md

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Configure database and API keys in `.env` or `config.py`
3. Run `python -m bot.scheduler` to start automation

## Extensibility
- Add new data sources or analysis modules as needed.
- All modules are designed to be independently testable and replaceable.
