import pandas as pd
import os
from db import get_connection

def export_trade_signals(filename='trade_signals.csv'):
    with get_connection() as conn:
        df = pd.read_sql_query('SELECT * FROM trades', conn)
        if df.empty:
            print('No trade signals to export.')
            return
        df.to_csv(filename, index=False)
        print(f'Trade signals exported to {filename}')

def export_watchlist(filename='watchlist.csv'):
    with get_connection() as conn:
        df = pd.read_sql_query('SELECT * FROM watchlist', conn)
        if df.empty:
            print('No watchlist data to export.')
            return
        df.to_csv(filename, index=False)
        print(f'Watchlist exported to {filename}')

def export_shortlist(filename='shortlist.csv'):
    with get_connection() as conn:
        df = pd.read_sql_query('SELECT * FROM shortlisted', conn)
        if df.empty:
            print('No shortlist data to export.')
            return
        df.to_csv(filename, index=False)
        print(f'Shortlist exported to {filename}')

if __name__ == "__main__":
    export_trade_signals()
    export_watchlist()
    export_shortlist()
