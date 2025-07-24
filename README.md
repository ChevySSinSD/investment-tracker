# Investment Tracker

Simple portfolio tracker with CSV import using FastAPI, SQLite, and basic HTML.

---

## 🚀 Features

- Upload CSVs of transactions (buy, sell, dividend)
- View transaction history in a table
- Backend built with FastAPI and SQLite
- Basic HTML templates using Jinja2
- Docker-ready for easy deployment

---

## 🛠 Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/investment-tracker.git
cd investment-tracker
```

### 2. Install dependencies

If running locally:

```bash
pip install -r requirements.txt
```

Or use Docker:

```bash
docker-compose up --build
```

---

## 🌐 Usage

### Import Transactions

Visit:

```
http://localhost:8000/import
```

Upload a CSV file in the following format:

```csv
date,ticker,quantity,price,transaction_type
2024-06-01,AAPL,10,185.50,buy
2024-06-15,AAPL,5,190.00,sell
2024-07-01,AAPL,0,5.00,dividend
```

- `date`: in YYYY-MM-DD format
- `ticker`: stock ticker symbol
- `quantity`: number of shares (can be 0 for dividends)
- `price`: price per share or dividend amount
- `transaction_type`: one of `buy`, `sell`, or `dividend`

### View Transactions

Visit:

```
http://localhost:8000/
```

You’ll see a table with all uploaded transactions.

---

## 📂 Project Structure

```
investment-tracker/
├── app/
│   ├── main.py          # FastAPI app
│   ├── models.py        # SQLAlchemy models
│   ├── crud.py          # DB operations
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # DB session setup
├── templates/           # HTML templates (Jinja2)
├── static/              # CSS/JS
├── data/                # SQLite database file
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔧 Next Steps

- Calculate portfolio value over time
- Fetch live prices using Yahoo Finance or another API
- Compute realized gains, XIRR
- Add authentication for multi-user support

---

## 📄 License

MIT License