from sqlalchemy import Column, Integer, String, Float, Date
from datetime import datetime
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    ticker = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    type = Column(String, nullable=False, default="buy")
    fee = Column(Float, nullable=True, default=0.0)
    currency = Column(String, nullable=True, default="USD")

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.utcnow().date, index=True)
    total_value = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    total_unrealized = Column(Float, nullable=False)
    total_realized = Column(Float, nullable=False)