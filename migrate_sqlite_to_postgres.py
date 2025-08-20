import pandas as pd
from sqlalchemy import create_engine, inspect

# Update these with your actual values
SQLITE_DB_PATH = 'trading_bot.db'
POSTGRES_URL = 'postgresql://caden:Cadentraders2023@caden.cncos20yym17.ap-south-1.rds.amazonaws.com:5432/caden'

# Create SQLAlchemy engines
sqlite_engine = create_engine(f'sqlite:///{SQLITE_DB_PATH}')
pg_engine = create_engine(POSTGRES_URL)

# Get all table names from SQLite
inspector = inspect(sqlite_engine)
tables = inspector.get_table_names()

for table in tables:
    print(f"Migrating table: {table}")
    df = pd.read_sql_table(table, sqlite_engine)
    # Write to PostgreSQL, append if table exists
    df.to_sql(table, pg_engine, if_exists='append', index=False)
    print(f"Table {table} migrated, {len(df)} rows.")

print("Migration complete!")
