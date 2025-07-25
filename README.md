# Investment Tracker

Simple self-hosted portfolio tracker with CSV import using FastAPI, SQLite, and basic HTML.

---

## 🚀 Features

- Upload CSVs of transactions (buy, sell, dividend)
- FIFO/LIFO cost basis tracking (FIFO default)
- Automatic daily portfolio snapshots
- Historical performance chart and snapshot table
- Uses Yahoo Finance for price data (with fallback for closed market days)
- Real-time portfolio dashboard
- Benchmark dropdown for comparison (e.g., SPY, VTI)
- Backend built with FastAPI and SQLite
- Clean HTML templates using Jinja2
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

## 🌐 Usage

### Import Transactions

Visit: http://localhost:8000/import

Upload a CSV file in the following format:

```csv
date,ticker,quantity,price,type,fee,currency
2024-06-01,AAPL,10,185.50,buy,0,USD
2024-06-15,AAPL,5,190.00,sell,0,USD
2024-07-01,AAPL,0,5.00,dividend,0,USD
```

- `date`: in YYYY-MM-DD format
- `ticker`: stock ticker symbol
- `quantity`: number of shares (can be 0 for dividends)
- `price`: price per share or dividend amount
- `type`: one of `buy`, `sell`, or `dividend`
- `fee` : fee charged for transaction
- `currency` : currency of transaction (default: USD)

## 📊 Performance & Snapshots

### Performance Dashboard
View portfolio performance over time: http://localhost:8000/performance

### Snapshot History Table
See daily snapshots of total value, cost, and gains: http://localhost:8000/performance/history

## 🔁 Background Tasks
- Daily snapshot logic runs at app startup to launch APScheduler 
- Portfolio snapshops backfilled after imports

## 📂 Project Structure

```
investment-tracker/
├── app/
│   ├── main.py          # FastAPI app
│   ├── models.py        # SQLAlchemy models
│   ├── crud.py          # DB operations
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # DB session setup
│   └── snapshots.py     # Portfolio performance snapshots
│   └── pricing.py     # yFinance pricing
├── templates/           # HTML templates (Jinja2)
├── static/              # CSS/JS
├── data/                # SQLite database file
├── requirements.txt
├── compose.yml
├── Dockerfile
└── README.md
```

---

## 🔧 Next Steps

- 📤 Export transactions as CSV
- Add support for multiple accounts
- Add support for manually tracked investments (for investments without data available via Yahoo! Finance)
- Improve frontend

---

## 📄 License

MIT License