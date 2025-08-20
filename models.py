from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from datetime import datetime
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

# About Us table for storing about us content
class AboutUs(Base):
    __tablename__ = 'about_us'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Use DATABASE_URL from environment variable for cloud deployment, fallback to local for dev
import os
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError("DATABASE_URL environment variable is not set. Please set it to your PostgreSQL connection string.")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
