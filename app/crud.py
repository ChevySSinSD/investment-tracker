from sqlalchemy.orm import Session
from . import models
from .schemas import TransactionCreate

def add_transaction(db: Session, txn: TransactionCreate):
    db_txn = models.Transaction(**txn.dict())
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn

def get_all_transactions(db: Session):
    return db.query(models.Transaction).order_by(models.Transaction.date).all()