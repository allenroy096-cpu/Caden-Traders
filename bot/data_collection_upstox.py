# All Upstox API code is disabled for this environment.
# If you need to enable Upstox integration, uncomment and configure the code below.
#
# try:
#     from upstox_api.api import Upstox, Session, OHLCInterval
# except ImportError:
#     Upstox = Session = OHLCInterval = None
# try:
#     from .config.upstox_config import UPSTOX_API_KEY, UPSTOX_API_SECRET, UPSTOX_REDIRECT_URI, UPSTOX_ACCESS_TOKEN
# except ImportError:
#     from bot.config.upstox_config import UPSTOX_API_KEY, UPSTOX_API_SECRET, UPSTOX_REDIRECT_URI, UPSTOX_ACCESS_TOKEN
# try:
#     from .config.models import SessionLocal, Trade
# except ImportError:
#     from bot.config.models import SessionLocal, Trade
# import datetime
#
# # Authenticate and create Upstox instance
# # (Assumes you have already obtained the access token)
# u = Upstox(UPSTOX_API_KEY, UPSTOX_API_SECRET)
# u.set_access_token(UPSTOX_ACCESS_TOKEN)
#
# def fetch_upstox_historical(symbol, exchange, start_date, end_date, interval='day'):
#     """
#     Fetch historical OHLC data from Upstox and store in DB.
#     symbol: e.g. 'NIFTY 50'
#     exchange: e.g. 'NSE_EQ'
#     interval: 'day', '15minute', etc.
#     """
#     interval_map = {
#         'day': OHLCInterval.Day_1,
#         '15minute': OHLCInterval.Min_15,
#         '5minute': OHLCInterval.Min_5
#     }
#     ohlc_interval = interval_map.get(interval, OHLCInterval.Day_1)
#     data = u.get_ohlc(
#         symbol,
#         exchange,
#         start_date,
#         end_date,
#         ohlc_interval
#     )
#     session = SessionLocal()
#     try:
#         for bar in data:
#             trade = Trade(
#                 symbol=symbol,
#                 trade_type='HIST',
#                 quantity=0,
#                 price=bar['close'],
#                 timestamp=bar['datetime']
#             )
#             session.add(trade)
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         print(f"DB Error: {e}")
#     finally:
#         session.close()
#     return data
#
# # Example usage (uncomment and set your credentials):
# # fetch_upstox_historical('NIFTY 50', 'NSE_EQ', datetime.date(2024,1,1), datetime.date(2024,8,1), 'day')
