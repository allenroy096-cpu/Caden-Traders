import sqlite3
from contextlib import closing

DB_PATH = 'trading_bot.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def setup_database():
    with closing(get_connection()) as conn:
        c = conn.cursor()
        # Table for storing stock price data
        c.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(symbol, date)
            )
        ''')
        # Table for watchlist
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                added_on TEXT NOT NULL,
                reason TEXT
            )
        ''')
        # Table for shortlisted trades
        c.execute('''
            CREATE TABLE IF NOT EXISTS shortlisted (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                consolidation_start TEXT,
                consolidation_end TEXT,
                breakout_date TEXT,
                volume_confirmed INTEGER,
                UNIQUE(symbol, consolidation_start, consolidation_end)
            )
        ''')
        # Table for trades (added for robustness)
        c.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                entry_date TEXT,
                entry_price REAL,
                stop_loss REAL,
                target REAL,
                position_size REAL,
                volume INTEGER
            )
        ''')
        conn.commit()

if __name__ == "__main__":
    setup_database()
    print("Database and tables created.")
