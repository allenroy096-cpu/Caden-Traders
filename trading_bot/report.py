import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection

# Generate a report for a given symbol
def plot_signals(symbol, start_date=None, end_date=None):
    with get_connection() as conn:
        query = '''
            SELECT s.date, s.close, i.rsi, i.macd, i.macdsignal
            FROM stock_prices s
            LEFT JOIN indicators i ON s.symbol = i.symbol AND s.date = i.date
            WHERE s.symbol = ?
            ORDER BY s.date ASC
        '''
        df = pd.read_sql_query(query, conn, params=(symbol,))
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        if df.empty:
            print(f"No data for {symbol} in the given range.")
            return
        fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        axs[0].plot(df['date'], df['close'], label='Close Price')
        axs[0].set_title(f'{symbol} Close Price')
        axs[0].legend()
        axs[1].plot(df['date'], df['rsi'], label='RSI', color='orange')
        axs[1].axhline(70, color='red', linestyle='--', alpha=0.5)
        axs[1].axhline(30, color='green', linestyle='--', alpha=0.5)
        axs[1].set_title('RSI (14)')
        axs[1].legend()
        axs[2].plot(df['date'], df['macd'], label='MACD', color='blue')
        axs[2].plot(df['date'], df['macdsignal'], label='Signal', color='magenta')
        axs[2].set_title('MACD & Signal')
        axs[2].legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Example usage: plot for RELIANCE.NS
    plot_signals('RELIANCE.NS')
