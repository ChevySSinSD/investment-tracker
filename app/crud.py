from sqlalchemy.orm import Session
from . import models, schemas

def create_transaction(db: Session, tx: schemas.TransactionCreate):
    db_tx = models.Transaction(**tx.dict())
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()
