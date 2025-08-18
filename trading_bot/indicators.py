import pandas as pd
import pandas_ta as ta
from db import get_connection

# Calculate and store indicators for each symbol
def update_indicators():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT DISTINCT symbol FROM stock_prices')
        symbols = [row[0] for row in c.fetchall()]
        for symbol in symbols:
            df = pd.read_sql_query(
                'SELECT date, open, high, low, close, volume FROM stock_prices WHERE symbol = ? ORDER BY date ASC',
                conn, params=(symbol,))
            if len(df) < 30:
                continue
            df['rsi'] = ta.rsi(df['close'], length=14)
            macd = ta.macd(df['close'])
            df['macd'] = macd['MACD_12_26_9']
            df['macdsignal'] = macd['MACDs_12_26_9']
            df['macdhist'] = macd['MACDh_12_26_9']
            # Store indicators in a new table
            c.execute('''
                CREATE TABLE IF NOT EXISTS indicators (
                    symbol TEXT,
                    date TEXT,
                    rsi REAL,
                    macd REAL,
                    macdsignal REAL,
                    macdhist REAL,
                    PRIMARY KEY (symbol, date)
                )
            ''')
            for _, row in df.iterrows():
                c.execute('''
                    INSERT OR REPLACE INTO indicators (symbol, date, rsi, macd, macdsignal, macdhist)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, row['date'],
                      row['rsi'] if not pd.isna(row['rsi']) else None,
                      row['macd'] if not pd.isna(row['macd']) else None,
                      row['macdsignal'] if not pd.isna(row['macdsignal']) else None,
                      row['macdhist'] if not pd.isna(row['macdhist']) else None))
        conn.commit()

if __name__ == "__main__":
    update_indicators()
    print("Indicators updated.")
