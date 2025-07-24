import yfinance as yf

def get_latest_price(ticker: str) -> float:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return float(price)
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0
