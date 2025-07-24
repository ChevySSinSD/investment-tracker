from sqlalchemy.orm import Session
from . import models, schemas
from .schemas import TransactionCreate

def transaction_exists(db: Session, txn: schemas.TransactionCreate) -> bool:
    return db.query(models.Transaction).filter_by(
        date=txn.date,
        ticker=txn.ticker.upper().strip(),  # normalize
        quantity=txn.quantity,
        price=txn.price,
        type=txn.type
    ).first() is not None

def add_transaction(db: Session, txn: schemas.TransactionCreate):
    """
    Add a new transaction to the database.

    Args:
        db (Session): SQLAlchemy database session.
        txn (TransactionCreate): Transaction data to be added.

    Returns:
        Transaction: The newly created Transaction object.
    """
    if transaction_exists(db, txn):
        print(f"Duplicate transaction skipped: {txn}")
        return False  # not added
    db_txn = models.Transaction(**txn.dict())
    db.add(db_txn)
    db.commit()
    return True

def get_all_transactions(db: Session, limit: int = 100, offset: int = 0):
    """
    Retrieve all transactions from the database, ordered by date, with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        limit (int): Maximum number of transactions to return.
        offset (int): Number of transactions to skip.

    Returns:
        List[Transaction]: List of Transaction objects ordered by date.
    """
    return db.query(models.Transaction).order_by(models.Transaction.date).offset(offset).limit(limit).all()