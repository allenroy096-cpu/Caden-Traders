# Print Python interpreter info for debugging
import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)

# Portfolio integration and analytics
from flask import Flask, render_template, request, jsonify
try:
    from .config.models import SessionLocal, AnalysisResult
except ImportError:
    from config.models import SessionLocal, AnalysisResult

app = Flask(__name__)


# --- STRATEGY TEST PAGE ROUTE ---
@app.route('/strategy_test')
def strategy_test():
    return render_template('strategy_test.html')

# API endpoint to serve strategy test signals with extra details
@app.route('/api/strategy_signals')
def api_strategy_signals():
    session = SessionLocal()
    signals = session.query(AnalysisResult).filter(AnalysisResult.result.contains('action')).order_by(AnalysisResult.created_at.desc()).limit(20).all()
    strategy_signals = []
    for s in signals:
        # Try to parse details if present in result
        try:
            res = eval(s.result) if s.result.strip().startswith('{') else {'action': s.result}
        except Exception:
            res = {'action': s.result}

        # Compute real metrics for each strategy result
        # For SMA: count BUY/SELL, win ratio, risk/reward
        sample_size = 0
        win_count = 0
        total_risk = 0
        total_reward = 0
        prev_action = None
        prev_price = None
        for key in ['action', 'result']:
            if key in res and isinstance(res[key], str):
                # Parse action and price from string if possible
                import re
                m = re.search(r"'action': '([A-Z]+)'.*'price': ([0-9.]+)", res[key])
                if m:
                    action = m.group(1)
                    price = float(m.group(2))
                    if action == 'BUY':
                        prev_action = 'BUY'
                        prev_price = price
                    elif action == 'SELL' and prev_action == 'BUY' and prev_price is not None:
                        sample_size += 1
                        reward = price - prev_price
                        risk = abs(reward) if reward < 0 else 1  # crude risk proxy
                        total_reward += reward
                        total_risk += risk
                        if reward > 0:
                            win_count += 1
                        prev_action = None
                        prev_price = None

        win_ratio = (win_count / sample_size) if sample_size else 0
        risk_reward = (total_reward / total_risk) if total_risk else 0

        res['sample_size'] = sample_size
        res['win_ratio'] = round(win_ratio, 2)
        res['risk_reward'] = round(risk_reward, 2)
        strategy_signals.append({
            'symbol': s.symbol,
            'result': str(res),
            'created_at': s.created_at.strftime('%Y-%m-%d') if s.created_at else ''
        })
    session.close()
    return jsonify({'strategy_signals': strategy_signals})

# ...rest of your routes and logic...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from .settings import DB_URL

Base = declarative_base()

class Holding(Base):
    __tablename__ = 'holdings'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    name = Column(String)
    quantity = Column(Float)
    avg_price = Column(Float)
    current_price = Column(Float)
    sector = Column(String)
    last_updated = Column(Date)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Create tables if not exist
def init_db():
    Base.metadata.create_all(engine)

# Add or update holding
def upsert_holding(session, symbol, name, quantity, avg_price, current_price, sector, last_updated):
    holding = session.query(Holding).filter_by(symbol=symbol).first()
    if holding:
        holding.quantity = quantity
        holding.avg_price = avg_price
        holding.current_price = current_price
        holding.sector = sector
        holding.last_updated = last_updated
    else:
        holding = Holding(symbol=symbol, name=name, quantity=quantity, avg_price=avg_price, current_price=current_price, sector=sector, last_updated=last_updated)
        session.add(holding)
    session.commit()
