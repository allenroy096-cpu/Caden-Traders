from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    asset_class = Column(String)
    sector = Column(String)
    buy_price = Column(Float)
    quantity = Column(Integer)
    # Add more fields as needed

# Use DATABASE_URL from environment variable for cloud deployment, fallback to local for dev
import os
db_url = os.environ.get('DATABASE_URL', 'postgresql://nifty_user:nifty_pass@localhost/nifty_db')
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
