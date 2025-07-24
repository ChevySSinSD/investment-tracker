from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    symbol: str
    date: date
    type: str
    quantity: float
    price: float

class Transaction(TransactionCreate):
    id: int

    class Config:
        orm_mode = True
