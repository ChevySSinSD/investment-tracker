from fastapi import FastAPI, Request, Depends, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from . import models, crud, schemas
from .database import engine, SessionLocal
from .pricing import get_latest_price
from io import StringIO
import csv

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
def read_portfolio(request: Request, db=Depends(get_db)):
    txns = crud.get_all_transactions(db)
    return templates.TemplateResponse("index.html", {"request": request, "transactions": txns})

@app.get("/import")
def show_import(request: Request):
    return templates.TemplateResponse("import.html", {"request": request})

@app.post("/import")
async def import_csv(request: Request,
                     file: UploadFile = File(...),
                     db=Depends(get_db)):
    content = await file.read()
    reader = csv.DictReader(StringIO(content.decode("utf-8")))
    for row in reader:
        txn = schemas.TransactionCreate(
            date=row["date"],
            ticker=row["ticker"],
            quantity=float(row["quantity"]),
            price=float(row["price"]),
            transaction_type=row.get("transaction_type", "buy")  # New line
        )
        crud.add_transaction(db, txn)
    message = "Uploaded {} transactions".format(reader.line_num - 1)
    return templates.TemplateResponse("import.html", {"request": request, "message": message})

    from .pricing import get_latest_price

@app.get("/")
def read_portfolio(request: Request, db=Depends(get_db)):
    txns = crud.get_all_transactions(db)

    holdings = {}
    for txn in txns:
        if txn.ticker not in holdings:
            holdings[txn.ticker] = 0
        if txn.transaction_type == "buy":
            holdings[txn.ticker] += txn.quantity
        elif txn.transaction_type == "sell":
            holdings[txn.ticker] -= txn.quantity

    portfolio = []
    for ticker, qty in holdings.items():
        if qty == 0:
            continue
        price = get_latest_price(ticker)
        portfolio.append({
            "ticker": ticker,
            "quantity": qty,
            "price": price,
            "value": qty * price
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "portfolio": portfolio,
        "transactions": txns
    })

@app.get("/")
def read_portfolio(request: Request, db=Depends(get_db)):
    txns = crud.get_all_transactions(db)

    holdings = {}
    for txn in txns:
        if txn.ticker not in holdings:
            holdings[txn.ticker] = 0
        if txn.transaction_type == "buy":
            holdings[txn.ticker] += txn.quantity
        elif txn.transaction_type == "sell":
            holdings[txn.ticker] -= txn.quantity

    portfolio = []
    for ticker, qty in holdings.items():
        if qty == 0:
            continue
        price = get_latest_price(ticker)
        portfolio.append({
            "ticker": ticker,
            "quantity": qty,
            "price": price,
            "value": qty * price
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "portfolio": portfolio,
        "transactions": txns
    })