
from db import setup_database
from watchlist import update_watchlist
from shortlist import update_shortlist
from trade_entry import update_trades
# from indicators import update_indicators
from export_reports import export_trade_signals, export_watchlist, export_shortlist

from data_fetcher import fetch_all_nifty500_zerodha

if __name__ == "__main__":
    setup_database()
    # Fetch and update all Nifty 500 OHLC from Zerodha (10 years)
    fetch_all_nifty500_zerodha()
    update_watchlist()
    update_shortlist()
    # update_indicators()
    update_trades()
    export_trade_signals()
    export_watchlist()
    export_shortlist()
    print("Automation complete. Database updated with Nifty 500 OHLC from Zerodha.")
