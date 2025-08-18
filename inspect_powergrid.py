import sqlite3

conn = sqlite3.connect('trading_bot.db')
cursor = conn.execute("SELECT date, open, high, low, close FROM stock_prices WHERE symbol='POWERGRID.NS' AND date >= '2024-01-22' AND date <= '2024-02-05' ORDER BY date")
for row in cursor:
    print(row)
conn.close()
