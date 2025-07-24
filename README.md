# Investment Tracker

A lightweight, self-hosted investment performance tracker built with FastAPI and SQLite.

## Features
- Add and view investment transactions (buy, sell, dividend)
- SQLite backend
- FastAPI auto docs

## Getting Started

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Access the docs: http://localhost:8000/docs

Or run with Docker:

```bash
docker build -t investment-tracker .
docker run -p 8000:8000 investment-tracker
```
