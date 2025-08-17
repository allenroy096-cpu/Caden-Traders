

# ...existing code...


# ...existing code...

# InstrumentTestResult model must be defined after Base

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Try both relative and absolute imports for db_config, and ignore linter warnings if unresolved
try:
    from .db_config import SQLALCHEMY_DATABASE_URI  # type: ignore[import]
except ImportError:
    from bot.config.db_config import SQLALCHEMY_DATABASE_URI  # type: ignore[import]

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    trade_type = Column(String(10))
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    headline = Column(String(255))
    content = Column(Text)
    source = Column(String(100))
    published_at = Column(DateTime)

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

class InstrumentTestResult(Base):
    __tablename__ = 'instrument_test_results'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    box_high = Column(Float)
    box_low = Column(Float)
    last_price = Column(Float)
    action = Column(String(10))
    test_type = Column(String(50))
    tested_at = Column(DateTime, default=datetime.utcnow)
