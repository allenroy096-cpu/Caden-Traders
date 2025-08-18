import pandas as pd
from db import get_connection

# Simple backtest: equity curve, win rate, avg win/loss, max drawdown
def backtest_trades(initial_capital=50000, output_csv='backtest_results.csv'):
    with get_connection() as conn:
        trades = pd.read_sql_query('SELECT * FROM trades ORDER BY entry_date ASC', conn)
        if trades.empty:
            print('No trades to backtest.')
            return
        # Simulate: assume each trade hits target or stop_loss randomly (for demo)
        import numpy as np
        np.random.seed(42)
        trades['outcome'] = np.random.choice(['win', 'loss'], size=len(trades), p=[0.6, 0.4])
        trades['exit_price'] = trades.apply(lambda row: row['target'] if row['outcome']=='win' else row['stop_loss'], axis=1)
        trades['pnl'] = (trades['exit_price'] - trades['entry_price']) * trades['position_size']
        trades['capital'] = initial_capital + trades['pnl'].cumsum()
        # Metrics
        total_return = trades['capital'].iloc[-1] - initial_capital
        win_rate = (trades['outcome']=='win').mean()
        avg_win = trades[trades['outcome']=='win']['pnl'].mean()
        avg_loss = trades[trades['outcome']=='loss']['pnl'].mean()
        max_drawdown = (trades['capital'].cummax() - trades['capital']).max()
        # Save results
        trades.to_csv(output_csv, index=False)
        print(f'Backtest results saved to {output_csv}')
        print(f'Total return: {total_return:.2f}')
        print(f'Win rate: {win_rate:.2%}')
        print(f'Avg win: {avg_win:.2f}, Avg loss: {avg_loss:.2f}')
        print(f'Max drawdown: {max_drawdown:.2f}')

if __name__ == "__main__":
    backtest_trades()
