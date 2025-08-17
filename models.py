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

# PostgreSQL connection string (edit host/db as needed)
engine = create_engine('postgresql://nifty_user:nifty_pass@localhost/nifty_db')
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
