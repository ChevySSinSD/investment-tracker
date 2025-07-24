from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, database, schemas, crud
import os

app = FastAPI()

if not os.path.exists("data"):
    os.makedirs("data")
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Investment Tracker API"}

@app.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, tx=tx)

@app.get("/transactions/", response_model=list[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="app/templates")

@app.get("/web", response_class=HTMLResponse)
def get_form(request: Request, db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db)
    return templates.TemplateResponse("index.html", {"request": request, "transactions": transactions})

@app.post("/web", response_class=HTMLResponse)
def submit_form(
    request: Request,
    symbol: str = Form(...),
    date: str = Form(...),
    type: str = Form(...),
    quantity: float = Form(...),
    price: float = Form(...),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    tx_data = schemas.TransactionCreate(
        symbol=symbol, date=datetime.fromisoformat(date).date(), type=type, quantity=quantity, price=price
    )
    crud.create_transaction(db=db, tx=tx_data)
    transactions = crud.get_transactions(db)
    return templates.TemplateResponse("index.html", {"request": request, "transactions": transactions})
