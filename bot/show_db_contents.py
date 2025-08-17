from bot.config.models import SessionLocal, Trade, News, AnalysisResult

# Query and print all trades
print("--- Trades ---")
session = SessionLocal()
trades = session.query(Trade).all()
for t in trades:
    print(f"{t.id}: {t.symbol} | {t.trade_type} | Qty: {t.quantity} | Price: {t.price} | Time: {t.timestamp}")

# Query and print all analysis results
print("\n--- Analysis Results ---")
results = session.query(AnalysisResult).all()
for r in results:
    print(f"{r.id}: {r.symbol} | {r.result} | Time: {r.created_at}")

# Query and print all news
print("\n--- News ---")
news = session.query(News).all()
for n in news:
    print(f"{n.id}: {n.headline} | Source: {n.source} | Time: {n.published_at}")
session.close()
