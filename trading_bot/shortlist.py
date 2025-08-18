from db import get_connection
from datetime import datetime, timedelta

# Parameters
daily_move_threshold = 0.05  # 5%
consolidation_days = 2

# Helper: check if a stock is in consolidation for N days
def is_consolidating(symbol, end_date, days=2, threshold=0.02):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT close FROM stock_prices
            WHERE symbol = ? AND date <= ?
            ORDER BY date DESC LIMIT ?
        ''', (symbol, end_date, days))
        closes = [row[0] for row in c.fetchall()]
        if len(closes) < days:
            return False
        max_close = max(closes)
        min_close = min(closes)
        return (max_close - min_close) / min_close < threshold

def update_shortlist():
    with get_connection() as conn:
        c = conn.cursor()
        # Get all watchlist stocks
        c.execute('SELECT symbol, added_on FROM watchlist')
        for symbol, added_on in c.fetchall():
            # Check for consolidation after added_on
            c.execute('''
                SELECT date FROM stock_prices
                WHERE symbol = ? AND date > ?
                ORDER BY date ASC
            ''', (symbol, added_on))
            dates = [row[0] for row in c.fetchall()]
            for i in range(len(dates) - consolidation_days):
                window = dates[i:i+consolidation_days]
                if is_consolidating(symbol, window[-1], consolidation_days):
                    # Add to shortlist
                    c.execute('''
                        INSERT OR IGNORE INTO shortlisted (symbol, consolidation_start, consolidation_end)
                        VALUES (?, ?, ?)
                    ''', (symbol, window[0], window[-1]))
                    break
        conn.commit()

if __name__ == "__main__":
    update_shortlist()
    print("Shortlist updated.")
