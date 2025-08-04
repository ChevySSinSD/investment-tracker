from . import models, crud
from .models import Transaction
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
        if txn.transaction_type == "buy":
            holdings[ticker] = holdings.get(ticker, 0) + qty
            total_invested[ticker] = total_invested.get(ticker, 0) + qty * txn.price + txn.fee
        elif txn.transaction_type == "sell":
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

    price_data = yf.download(symbols, start=first_date, end=last_date + timedelta(days=1))["Close"]
    if isinstance(price_data, pd.Series):
        price_data = price_data.to_frame()
    
    last_price = {}  # Ticker -> last known price

    current_date = first_date
    while current_date <= last_date:
        txns = db.query(models.Transaction).filter(models.Transaction.date <= current_date).order_by(models.Transaction.date).all()

        lots = {}  # {ticker: list of (qty, cost per share)}
        holdings = {}
        total_value = 0
        total_cost = 0
        total_realized = 0

        for txn in txns:
            t = txn.ticker.upper()
            if t not in lots:
                lots[t] = []

            if txn.transaction_type == "buy":
                lots[t].append([txn.quantity, txn.price])
            elif txn.transaction_type == "sell":
                qty_to_sell = txn.quantity
                cost_basis = 0
                proceeds = qty_to_sell * txn.price

                while qty_to_sell > 0 and lots[t]:
                    lot_qty, lot_price = lots[t][0]
                    if lot_qty <= qty_to_sell:
                        cost_basis += lot_qty * lot_price
                        qty_to_sell -= lot_qty
                        lots[t].pop(0)
                    else:
                        cost_basis += qty_to_sell * lot_price
                        lots[t][0][0] -= qty_to_sell
                        qty_to_sell = 0

                realized = proceeds - cost_basis
                total_realized += realized

        for ticker, qty_price_list in lots.items():
            qty = sum(qty for qty, _ in qty_price_list)
            cost = sum(qty * price for qty, price in qty_price_list)

            try:
                price = price_data[ticker].get(current_date.strftime("%Y-%m-%d"))
                if price:
                    last_price[ticker] = price
                else:
                    price = last_price.get(ticker)

                if price and qty > 0:
                    total_value += qty * price
                    total_cost += cost
            except Exception:
                continue

        total_unrealized = total_value - total_cost

        snapshot = models.PortfolioSnapshot(
            date=current_date,
            total_value=round(total_value, 2),
            total_cost=round(total_cost, 2),
            total_unrealized=round(total_unrealized, 2),
            total_realized=round(total_realized, 2)
        )
        db.merge(snapshot)

        current_date += timedelta(days=1)

    db.commit()