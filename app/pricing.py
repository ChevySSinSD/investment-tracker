import yfinance as yf

def get_latest_price(ticker: str):
    """
    Fetch the latest closing price for the given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1d")
        if df.empty or "Close" not in df or df["Close"].isna().all():
            df = stock.history(period="5d")
        close_prices = df["Close"].dropna()
        price = close_prices.iloc[-1]
        as_of = close_prices.index[-1].strftime("%Y-%m-%d")
        return float(price), as_of
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return 0.0, None

def get_historical_prices(ticker: str, days: int = 30):
    """
    Fetch historical closing prices for the past `days` days.
    Returns: (labels, prices)
        labels: list of dates (e.g., ["2024-07-01", "2024-07-02", ...])
        prices: list of prices (floats)
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=f"{days}d")
        if df.empty:
            return [], []
        labels = df.index.strftime("%Y-%m-%d").tolist()
        prices = df["Close"].round(2).tolist()
        return labels, prices
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return [], []
