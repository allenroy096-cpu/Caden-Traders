import pandas as pd
from datetime import datetime
try:
    from .config.models import SessionLocal, AnalysisResult
except ImportError:
    from config.models import SessionLocal, AnalysisResult

# Analyzes data for trade opportunities and risks

def analyze_opportunities_and_store(holdings, price_data):
    opportunities = analyze_opportunities(holdings, price_data)
    session = SessionLocal()
    try:
        for opp in opportunities:
            result = AnalysisResult(symbol=opp['symbol'], result=str(opp))
            session.add(result)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"DB Error: {e}")
    finally:
        session.close()
    return opportunities
def analyze_opportunities(holdings, price_data):
    opportunities = []
    for h in holdings:
        symbol = h.symbol
        if symbol in price_data:
            hist = price_data[symbol]
            if len(hist) > 30:
                recent = hist['Close'][-30:]
                mean = recent.mean()
                last = recent.iloc[-1]
                # Example: If price is 10% below 30-day mean, flag as opportunity
                if last < mean * 0.9:
                    opportunities.append({
                        'symbol': symbol,
                        'reason': 'Price 10% below 30-day mean',
                        'current': last,
                        'mean': mean
                    })
    return opportunities

# Example: Risk analysis (volatility, drawdown)
def analyze_risk(holdings, price_data):
    risks = []
    for h in holdings:
        symbol = h.symbol
        if symbol in price_data:
            hist = price_data[symbol]
            if len(hist) > 30:
                returns = hist['Close'].pct_change().dropna()
                volatility = returns.std()
                drawdown = (hist['Close'] / hist['Close'].cummax() - 1).min()
                risks.append({
                    'symbol': symbol,
                    'volatility': volatility,
                    'max_drawdown': drawdown
                })
    return risks
