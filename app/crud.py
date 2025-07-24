from sqlalchemy.orm import Session
from collections import deque
from . import models, schemas
from .schemas import TransactionCreate
from .models import Transaction

def compute_realized_gains(db: Session, ticker: str, method: str = "fifo") -> float:
    """
    Compute total realized gains for a given ticker using FIFO or LIFO.
    """
    buys = []
    sells = []

    txns = db.query(Transaction).filter(Transaction.ticker == ticker).order_by(Transaction.date).all()

    for txn in txns:
        if txn.type == "buy":
            buys.append({
                "date": txn.date,
                "quantity": txn.quantity,
                "price": txn.price,
                "remaining": txn.quantity
            })
        elif txn.type == "sell":
            sells.append({
                "date": txn.date,
                "quantity": txn.quantity,
                "price": txn.price
            })

    if method == "fifo":
        stack = deque(buys)  # oldest first
    elif method == "lifo":
        stack = deque(reversed(buys))  # newest first
    else:
        raise ValueError("Method must be 'fifo' or 'lifo'")

    realized_gain = 0.0

    for sell in sells:
        qty_to_match = sell["quantity"]
        sell_price = sell["price"]

        while qty_to_match > 0 and stack:
            lot = stack[0]
            match_qty = min(lot["remaining"], qty_to_match)
            gain = (sell_price - lot["price"]) * match_qty
            realized_gain += gain

            lot["remaining"] -= match_qty
            qty_to_match -= match_qty

            if lot["remaining"] == 0:
                stack.popleft()

    return round(realized_gain, 2)

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