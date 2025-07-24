from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(Date)
    type = Column(String)  # e.g., 'buy', 'sell', 'dividend'
    quantity = Column(Float)
    price = Column(Float)
