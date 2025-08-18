import sqlite3
conn = sqlite3.connect('trading_bot.db')
cursor = conn.execute("SELECT MIN(date), MAX(date) FROM stock_prices")
print(cursor.fetchone())
conn.close()
