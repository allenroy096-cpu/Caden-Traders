import pandas as pd
from db import get_connection

# Analyze sector performance over a rolling window
def sector_rotation_report(window=20, output_csv='sector_rotation.csv'):
    with get_connection() as conn:
        df = pd.read_sql_query('SELECT symbol, date, close FROM stock_prices', conn)
        # You must have a mapping from symbol to sector
        sector_map = {
            'RELIANCE.NS': 'Oil & Gas', 'TCS.NS': 'IT', 'HDFCBANK.NS': 'Banking', 'ICICIBANK.NS': 'Banking',
            'INFY.NS': 'IT', 'HINDUNILVR.NS': 'FMCG', 'ITC.NS': 'FMCG', 'LT.NS': 'Infra', 'SBIN.NS': 'Banking',
            # ...add more as needed
        }
        df['sector'] = df['symbol'].map(sector_map)
        df = df.dropna(subset=['sector'])
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        # Calculate sector returns
        pivot = df.pivot(index='date', columns='sector', values='close')
        sector_returns = pivot.pct_change(window)
        sector_strength = sector_returns.rolling(window).mean()
        latest = sector_strength.iloc[-1].sort_values(ascending=False)
        latest.to_csv(output_csv, header=['strength'])
        print(f"Sector rotation report saved to {output_csv}")

if __name__ == "__main__":
    sector_rotation_report()
