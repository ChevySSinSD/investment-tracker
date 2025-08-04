from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    ticker = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="USD")
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="transactions")

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.utcnow().date, index=True)
    total_value = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    total_unrealized = Column(Float, nullable=False)
    total_realized = Column(Float, nullable=False)