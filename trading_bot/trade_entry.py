from db import get_connection
from datetime import datetime, timedelta

# Parameters
risk_per_trade = 0.03  # 3% of position
reward_multiple = 3    # 3x risk
max_position_pct = 0.10  # 10% of total capital
TOTAL_CAPITAL = 50000

# Helper: get breakout candidates from shortlist
def get_breakout_candidates():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT symbol, consolidation_end FROM shortlisted
        ''')
        candidates = c.fetchall()
        breakout_list = []
        for symbol, end_date in candidates:
            # Get the high of the consolidation period
            c.execute('''
                SELECT MAX(high) FROM stock_prices WHERE symbol = ? AND date <= ?
            ''', (symbol, end_date))
            high = c.fetchone()[0]
            # Get the next day's close and volume
            c.execute('''
                SELECT date, close, volume FROM stock_prices WHERE symbol = ? AND date > ? ORDER BY date ASC LIMIT 1
            ''', (symbol, end_date))
            row = c.fetchone()
            if row:
                date, close, volume = row
                if close > high:
                    breakout_list.append((symbol, date, close, high, volume))
        return breakout_list

def calculate_position_size(entry_price, stop_loss):
    risk_amount = TOTAL_CAPITAL * risk_per_trade
    position_size = risk_amount / abs(entry_price - stop_loss)
    max_position = TOTAL_CAPITAL * max_position_pct / entry_price
    return min(position_size, max_position)

def update_trades():
    breakouts = get_breakout_candidates()
    with get_connection() as conn:
        c = conn.cursor()
        for symbol, date, close, high, volume in breakouts:
            # Risk: 2-4% below entry (use 3% for now)
            stop_loss = close * (1 - risk_per_trade)
            target = close + reward_multiple * (close - stop_loss)
            position_size = calculate_position_size(close, stop_loss)
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
            c.execute('''
                INSERT OR IGNORE INTO trades (symbol, entry_date, entry_price, stop_loss, target, position_size, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, date, close, stop_loss, target, position_size, volume))
        conn.commit()

if __name__ == "__main__":
    update_trades()
    print("Trade entries updated.")
