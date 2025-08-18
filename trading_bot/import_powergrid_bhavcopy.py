import os
import pandas as pd
import sqlite3
from datetime import datetime

DB_PATH = 'trading_bot.db'
SYMBOL = 'POWERGRID'
NSE_SYMBOL = 'POWERGRID'

# Directory where Bhavcopy CSVs are downloaded
BHAVCOPY_DIR = './bhavcopy/'  # Place your downloaded CSVs here

def import_bhavcopy():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    files = [f for f in os.listdir(BHAVCOPY_DIR) if f.endswith('.csv')]
    files.sort()  # Ensure chronological order
    for fname in files:
        fpath = os.path.join(BHAVCOPY_DIR, fname)
        try:
            df = pd.read_csv(fpath)
            row = df[df['SYMBOL'] == NSE_SYMBOL]
            if not row.empty:
                open_ = float(row['OPEN'].values[0])
                high = float(row['HIGH'].values[0])
                low = float(row['LOW'].values[0])
                close = float(row['CLOSE'].values[0])
                volume = int(row['TOTTRDQTY'].values[0])
                # Extract date from filename (EQddmmyyyy.csv)
                date_str = fname[2:10]  # ddmmyyyy
                db_date = datetime.strptime(date_str, '%d%m%Y').strftime('%Y-%m-%d')
                c.execute('''
                    INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (SYMBOL + '.NS', db_date, open_, high, low, close, volume))
                print(f"Imported {SYMBOL}.NS for {db_date}: open={open_}, high={high}, low={low}, close={close}, volume={volume}")
        except Exception as e:
            print(f"Error processing {fname}: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_bhavcopy()
    print("Done importing POWERGRID data from Bhavcopy CSVs.")
