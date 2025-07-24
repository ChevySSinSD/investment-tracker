from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from io import StringIO
import csv

from app import models, crud, schemas
from .database import engine, SessionLocal
from .pricing import get_latest_price, get_historical_prices
from .crud import compute_realized_gains

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_portfolio(request: Request, db: Session = Depends(get_db)):
    txns = crud.get_all_transactions(db)

    holdings = {}
    for txn in txns:
        if txn.ticker not in holdings:
            holdings[txn.ticker] = 0
        if txn.type == "buy":
            holdings[txn.ticker] += txn.quantity
        elif txn.type == "sell":
            holdings[txn.ticker] -= txn.quantity

    portfolio = []
    for ticker, qty in holdings.items():
        if qty == 0:
            continue
        price, as_of = get_latest_price(ticker)
        portfolio.append({
            "ticker": ticker,
            "quantity": qty,
            "price": price,
            "value": round(qty * price, 2),
            "as_of": as_of
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "portfolio": portfolio,
        "transactions": txns
    })

@app.get("/import")
def show_import(request: Request):
    return templates.TemplateResponse("import.html", {"request": request})

@app.post("/import")
async def import_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Imports transactions from a CSV file.

    Expected CSV columns: date, ticker, quantity, price, type (optional, defaults to 'buy').
    Each row is validated; if a row is missing required fields or contains invalid data,
    an error message is displayed indicating the row number and error.
    Duplicate transactions (same date, ticker, quantity, price, type) are skipped.
    """
    content = await file.read()
    try:
        reader = csv.DictReader(StringIO(content.decode("utf-8")))
        count = 0
        skipped = 0
        for row in reader:
            try:
                txn = schemas.TransactionCreate(
                    date=row["date"],
                    ticker=row["ticker"].strip().upper(),  # normalize here
                    quantity=float(row["quantity"]),
                    price=float(row["price"]),
                    type=row.get("type", "buy").lower(),
                    fee=float(row.get("fee", 0.0)),
                    currency=row.get("currency", "USD").upper()
            )
                added = crud.add_transaction(db, txn)
                if added:
                    count += 1
                else:
                    skipped += 1
            except (KeyError, ValueError) as e:
                return templates.TemplateResponse("import.html", {
                    "request": request,
                    "message": f"Error in row {reader.line_num}: {e}"
                })
        message = f"Uploaded {count} transactions"
        if skipped:
            message += f" (Skipped {skipped} duplicates)"
    except Exception as e:
        message = f"Failed to process CSV file: {e}"
    return templates.TemplateResponse("import.html", {"request": request, "message": message})

@app.get("/chart/{ticker}")
def show_chart(ticker: str, request: Request):
    labels, prices = get_historical_prices(ticker)
    return templates.TemplateResponse("chart.html", {
        "request": request,
        "ticker": ticker.upper(),
        "labels": labels,
        "prices": prices
    })

@app.get("/gains/{ticker}")
def gains_view(ticker: str, db: Session = Depends(get_db)):
    gain_fifo = compute_realized_gains(db, ticker.upper(), method="fifo")
    gain_lifo = compute_realized_gains(db, ticker.upper(), method="lifo")
    return {
        "ticker": ticker.upper(),
        "realized_gain_fifo": gain_fifo,
        "realized_gain_lifo": gain_lifo
    }

@app.get("/dashboard", response_class=HTMLResponse)
def portfolio_dashboard(request: Request, db: Session = Depends(get_db)):
    txns = crud.get_all_transactions(db)

    holdings = {}
    total_invested = {}
    for txn in txns:
        ticker = txn.ticker.strip().upper()
        qty = float(txn.quantity)
        if txn.type == "buy":
            holdings[ticker] = holdings.get(ticker, 0) + qty
            total_invested[ticker] = total_invested.get(ticker, 0) + qty * txn.price + txn.fee
        elif txn.type == "sell":
            holdings[ticker] = holdings.get(ticker, 0) - qty  # reduce quantity

    portfolio = []
    total_value = 0
    total_cost = 0
    for ticker, qty in holdings.items():
        if qty <= 0:
            continue
        price, as_of = get_latest_price(ticker)
        value = qty * price
        cost = total_invested.get(ticker, 0)
        gain = value - cost
        total_value += value
        total_cost += cost

        realized_gain = compute_realized_gains(db, ticker, method="fifo")
        portfolio.append({
            "ticker": ticker,
            "quantity": qty,
            "price": price,
            "value": round(value, 2),
            "cost": round(cost, 2),
            "unrealized_gain": round(gain, 2),
            "realized_gain": realized_gain,
            "as_of": as_of
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "portfolio": portfolio,
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_unrealized": round(total_value - total_cost, 2),
        "total_realized": sum(p["realized_gain"] for p in portfolio)
    })