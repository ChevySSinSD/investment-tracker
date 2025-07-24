from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    date: date
    ticker: str
    quantity: float
    price: float