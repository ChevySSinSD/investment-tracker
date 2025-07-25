from . import models, crud
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, date
from .pricing import get_latest_price
import yfinance as yf
import pandas as pd

def save_daily_snapshot_if_needed(db: Session):
    today = date.today()
    exists = db.query(models.PortfolioSnapshot).filter(models.PortfolioSnapshot.date == today).first()
    if exists:
        return  # Don't save duplicate snapshots
    
    txns = db.query(Transaction).all()
    
    holdings = {}
    total_invested = {}
    for txn in txns:
        ticker = txn.ticker.strip().upper()
        qty = float(txn.quantity)
        if txn.type == "buy":
            holdings[ticker] = holdings.get(ticker, 0) + qty
            total_invested[ticker] = total_invested.get(ticker, 0) + qty * txn.price + txn.fee
        elif txn.type == "sell":
            holdings[ticker] = holdings.get(ticker, 0) - qty

    total_value = 0
    total_cost = 0
    for ticker, qty in holdings.items():
        if qty <= 0:
            continue
        price, _ = get_latest_price(ticker)
        value = qty * price
        cost = total_invested.get(ticker, 0)
        total_value += value
        total_cost += cost

    total_realized = sum(
        compute_realized_gains(db, ticker, method="fifo")
        for ticker in holdings.keys()
    )

    snapshot = PortfolioSnapshot(
        total_value=round(total_value, 2),
        total_cost=round(total_cost, 2),
        total_unrealized=round(total_value - total_cost, 2),
        total_realized=round(total_realized, 2),
    )
    db.add(snapshot)
    db.commit()

def backfill_snapshots(db: Session):
    first_date = db.query(func.min(models.Transaction.date)).scalar()
    last_date = db.query(func.max(models.Transaction.date)).scalar()
    if not first_date or not last_date:
        return

    tickers = db.query(models.Transaction.ticker).distinct()
    symbols = [t[0].upper() for t in tickers]

    price_data = yf.download(symbols, start=first_date, end=last_date + timedelta(days=1))["Adj Close"]
    if isinstance(price_data, pd.Series):
        price_data = price_data.to_frame()

    current_date = first_date
    while current_date <= last_date:
        txns = (
            db.query(models.Transaction)
            .filter(models.Transaction.date <= current_date)
            .order_by(models.Transaction.date)
            .all()
        )

        current_holdings = {}
        for txn in txns:
            t = txn.ticker.upper()
            if t not in current_holdings:
                current_holdings[t] = 0
            if txn.type == "buy":
                current_holdings[t] += txn.quantity
            elif txn.type == "sell":
                current_holdings[t] -= txn.quantity

        total_value = 0
        for ticker, qty in current_holdings.items():
            try:
                price = price_data[ticker].get(current_date.strftime("%Y-%m-%d"))
                if price and qty > 0:
                    total_value += qty * price
            except Exception:
                continue

        if total_value > 0:
            snapshot = models.PortfolioSnapshot(date=current_date, total_value=round(total_value, 2))
            db.merge(snapshot)

        current_date += timedelta(days=1)

    db.commit()