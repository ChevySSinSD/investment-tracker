from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    date: date
    ticker: str
    quantity: float
    price: float
    type: str = "buy"
    fee: float = 0.0
    currency: str = "USD"