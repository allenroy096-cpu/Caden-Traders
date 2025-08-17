# Database configuration for PostgreSQL
DB_CONFIG = {
    'user': 'nifty_user',
    'password': 'nifty_pass',
    'host': 'localhost',
    'port': '5432',
    'database': 'nifty_db'
}

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
