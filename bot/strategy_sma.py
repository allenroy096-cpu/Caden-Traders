try:
    from .config.models import SessionLocal, Trade, AnalysisResult  # type: ignore[import]
except ImportError:
    from bot.config.models import SessionLocal, Trade, AnalysisResult  # type: ignore[import]
import pandas as pd
from datetime import datetime

# Example: Simple moving average crossover strategy
# Buy when price crosses above 20-day MA, sell when below

def run_sma_strategy(symbol='NIFTY 50'):
    session = SessionLocal()
    trades = session.query(Trade).filter(Trade.symbol == symbol).order_by(Trade.timestamp).all()
    if not trades:
        print("No data for symbol.")
        session.close()
        return []
    df = pd.DataFrame([
        {'timestamp': t.timestamp, 'price': t.price} for t in trades
    ])
    df.set_index('timestamp', inplace=True)
    df['ma20'] = df['price'].rolling(window=20).mean()
    df['signal'] = 0
    df['signal'][20:] = (df['price'][20:] > df['ma20'][20:]).astype(int)
    df['position'] = df['signal'].diff()
    signals = []
    for idx, row in df.iterrows():
        if row['position'] == 1:
            signals.append({'symbol': symbol, 'action': 'BUY', 'price': row['price'], 'date': idx})
        elif row['position'] == -1:
            signals.append({'symbol': symbol, 'action': 'SELL', 'price': row['price'], 'date': idx})
    # Store results in DB
    for sig in signals:
        result = AnalysisResult(symbol=sig['symbol'], result=str(sig), created_at=sig['date'])
        session.add(result)
    session.commit()
    session.close()
    return signals

if __name__ == "__main__":
    signals = run_sma_strategy()
    print(signals)
