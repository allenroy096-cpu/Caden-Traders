from db import get_connection
from datetime import datetime, timedelta

# Parameters
weekly_move_threshold = 0.03  # 3%
lookback_days = 7
consolidation_days = 2

# Add logic to scan for 5% movers and consolidation
def update_watchlist():
    with get_connection() as conn:
        c = conn.cursor()
        # Find stocks with 5% move over the last week
        c.execute('SELECT MIN(date), MAX(date) FROM stock_prices')
        min_date, max_date = c.fetchone()
        min_date = datetime.strptime(min_date, '%Y-%m-%d')
        max_date = datetime.strptime(max_date, '%Y-%m-%d')
        added = 0
        week_count = 0
        # For each week in the dataset
        current = min_date
        while current < max_date:
            week_start = current
            week_end = week_start + timedelta(days=6)
            week_end_str = week_end.strftime('%Y-%m-%d')
            week_start_str = week_start.strftime('%Y-%m-%d')
            c.execute('''
                SELECT symbol, MIN(low), MAX(high)
                FROM stock_prices
                WHERE date BETWEEN ? AND ?
                GROUP BY symbol
            ''', (week_start_str, week_end_str))
            rows = c.fetchall()
            for symbol, week_low, week_high in rows:
                if week_low and week_high and (week_high - week_low) / week_low >= weekly_move_threshold:
                    c.execute('''
                        INSERT OR IGNORE INTO watchlist (symbol, added_on, reason)
                        VALUES (?, ?, ?)
                    ''', (symbol, week_end_str, f'{int(weekly_move_threshold*100)}% weekly high-low move'))
                    print(f"Added {symbol} to watchlist for week {week_start_str} to {week_end_str}: low={week_low}, high={week_high}")
                    added += 1
            week_count += 1
            current += timedelta(days=7)
        conn.commit()
        print(f"Scanned {week_count} weeks for {int(weekly_move_threshold*100)}% weekly high-low move.")
        if added == 0:
            print(f"No stocks met the {int(weekly_move_threshold*100)}% weekly high-low move threshold.")

if __name__ == "__main__":
    update_watchlist()
    print("Watchlist updated.")
