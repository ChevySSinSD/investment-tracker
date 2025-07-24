# Investment Tracker

Simple portfolio tracker with CSV import using FastAPI, SQLite, and basic HTML.

## Usage

1. Build & run:
   ```bash
   docker-compose up --build
   ```

2. Visit `http://localhost:8000/import` to upload transactions CSV:
   ```
   date,ticker,quantity,price
   2024-06-01,AAPL,10,185.50
   ```

3. View at `http://localhost:8000/`.

---

## 🚀 Next Steps

- Fetch live prices and calculate value/gains.
- Add XIRR/net gain summary.
- Enhance styling or switch to a JS frontend.

Contributions welcome!