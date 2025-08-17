import pandas as pd
from datetime import datetime

# Log decisions and outcomes
def log_decision(symbol, action, reason, outcome=None, log_file='decisions_log.csv'):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'action': action,
        'reason': reason,
        'outcome': outcome
    }
    try:
        df = pd.read_csv(log_file)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([entry])
    df.to_csv(log_file, index=False)

# Placeholder for self-learning (e.g., reinforcement learning)
def self_learn_from_logs(log_file='decisions_log.csv'):
    try:
        df = pd.read_csv(log_file)
        # Implement learning logic here (e.g., reward, Q-learning, etc.)
        # For now, just print summary
        print(df.groupby(['action', 'outcome']).size())
    except Exception as e:
        print(f"Learning error: {e}")
