
# Updated: Fetch 10 years of daily data for all Nifty 500 stocks using yfinance


from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
from db import get_connection

NIFTY_500_SYMBOLS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS', 'HINDUNILVR.NS', 'ITC.NS', 'LT.NS', 'SBIN.NS', 'KOTAKBANK.NS',
    'BHARTIARTL.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'HCLTECH.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'WIPRO.NS',
    'BAJAJFINSV.NS', 'POWERGRID.NS', 'NTPC.NS', 'TATAMOTORS.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'ADANITRANS.NS', 'AMBUJACEM.NS', 'APOLLOHOSP.NS',
    'AUROPHARMA.NS', 'BAJAJ-AUTO.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'BERGEPAINT.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'BRITANNIA.NS', 'CHOLAFIN.NS', 'CIPLA.NS',
    'COALINDIA.NS', 'COLPAL.NS', 'DABUR.NS', 'DIVISLAB.NS', 'DLF.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS', 'GLAND.NS', 'GODREJCP.NS',
    'GRASIM.NS', 'HAVELLS.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDPETRO.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'IDFCFIRSTB.NS', 'IGL.NS',
    'INDIGO.NS', 'INDUSINDBK.NS', 'INDUSTOWER.NS', 'IOC.NS', 'IRCTC.NS', 'ITC.NS', 'JINDALSTEL.NS', 'JSWSTEEL.NS', 'JUBLFOOD.NS', 'L&TFH.NS',
    'LTI.NS', 'LUPIN.NS', 'M&M.NS', 'M&MFIN.NS', 'MANAPPURAM.NS', 'MARICO.NS', 'MOTHERSUMI.NS', 'MRF.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS',
    'NESTLEIND.NS', 'NMDC.NS', 'OBEROIRLTY.NS', 'ONGC.NS', 'PAGEIND.NS', 'PEL.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'PIIND.NS', 'PNB.NS',
    'POLYCAB.NS', 'POWERGRID.NS', 'PVR.NS', 'RAMCOCEM.NS', 'RBLBANK.NS', 'RECLTD.NS', 'SAIL.NS', 'SBICARD.NS', 'SHREECEM.NS', 'SIEMENS.NS',
    'SRF.NS', 'SRTRANSFIN.NS', 'SYNGENE.NS', 'TATACHEM.NS', 'TATACONSUM.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TCS.NS', 'TECHM.NS', 'TORNTPHARM.NS',
    'TORNTPOWER.NS', 'TRENT.NS', 'TVSMOTOR.NS', 'UBL.NS', 'ULTRACEMCO.NS', 'UPL.NS', 'VEDL.NS', 'VOLTAS.NS', 'WHIRLPOOL.NS', 'WIPRO.NS',
    'ZEEL.NS', 'ZYDUSLIFE.NS'
    # ... (add the rest of the Nifty 500 symbols as needed)
]


# Zerodha API fetch for all Nifty 500
def fetch_all_nifty500_zerodha():
    load_dotenv()
    api_key = os.getenv("KITE_API_KEY")
    access_token = os.getenv("KITE_ACCESS_TOKEN")
    db_path = 'trading_bot.db'
    exchange = 'NSE'
    interval = 'day'
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    print("Fetching instrument list from Zerodha...")
    instruments = kite.instruments(exchange)
    symbol_to_token = {inst['tradingsymbol']: inst['instrument_token'] for inst in instruments if inst['exchange'] == exchange}
    for symbol in NIFTY_500_SYMBOLS:
        base_symbol = symbol.replace('.NS', '')
        inst_token = symbol_to_token.get(base_symbol)
        if not inst_token:
            print(f"Instrument token for {symbol} not found. Skipping.")
            continue
        try:
            data = kite.historical_data(inst_token, start_date, end_date, interval)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        for row in data:
            db_date = row['date'].strftime('%Y-%m-%d')
            open_ = row['open']
            high = row['high']
            low = row['low']
            close = row['close']
            volume = row['volume']
            c.execute('''
                INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, db_date, open_, high, low, close, volume))
        conn.commit()
        conn.close()
        print(f"Inserted {symbol} for {len(data)} days.")
    print("Done fetching and populating Nifty 500 OHLC data from Zerodha for 2020-2024.")




