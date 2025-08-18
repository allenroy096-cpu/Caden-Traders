import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection

def plot_equity_curve(csv_file='backtest_results.csv', output_img='equity_curve.png'):
    df = pd.read_csv(csv_file)
    if 'capital' not in df:
        print('No equity curve data found.')
        return
    plt.figure(figsize=(12,6))
    plt.plot(df['entry_date'], df['capital'], label='Equity Curve', color='blue')
    plt.title('Backtest Equity Curve')
    plt.xlabel('Trade Date')
    plt.ylabel('Portfolio Value')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_img)
    plt.show()
    print(f'Equity curve saved to {output_img}')

if __name__ == "__main__":
    plot_equity_curve()
