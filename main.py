# main.py
# yfinance API connection and data fetching utilities

import sys
import pandas as pd
import yfinance as yf


_DATA_PERIOD_MAP = {
    "1m":  {200: "1d", 1000: "5d", None: "max"},
    "2m":  {100: "1d", 500: "5d", 2000: "1mo", None: "max"},
    "5m":  {40: "1d", 200: "5d", 800: "1mo", None: "max"},
    "15m": {13: "1d", 65: "5d", 260: "1mo", None: "max"},
    "30m": {6: "1d", 32: "5d", 130: "1mo", None: "max"},
    "90m": {2: "1d", 10: "5d", 43: "1mo", None: "max"},
    "60m": {3: "1d", 16: "5d", 65: "1mo", 200: "3mo", 400: "6mo",
            800: "1y", 1600: "2y", None: "max"},
    "1h":  {3: "1d", 16: "5d", 65: "1mo", 200: "3mo", 400: "6mo",
            800: "1y", 1600: "2y", None: "max"},
    "1d":  {30: "3mo", 60: "6mo", 120: "1y", 240: "2y", 600: "5y", None: "10y"},
    "5d":  {6: "3mo", 13: "6mo", 26: "1y", 52: "2y", 130: "5y", None: "10y"},
    "1wk": {12: "6mo", 26: "1y", 52: "2y", 130: "5y", None: "10y"},
    "1mo": {6: "1y", 12: "2y", 30: "5y", None: "10y"},
    "3mo": {2: "1y", 4: "2y", 10: "5y", None: "10y"},
}

_VALID_INTERVALS = frozenset(_DATA_PERIOD_MAP.keys())


def _data_period(window: int, interval: str = "1d") -> str:
    """Map a lookback window + interval to a yfinance period string.

    Uses conservative thresholds so rolling calculations always
    have enough data after discarding NaN rows.

    Args:
        window: Requested lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").

    Returns:
        A yfinance-compatible period string (e.g. "3mo", "1y").

    Raises:
        ValueError: If interval is not recognised.
    """
    thresholds = _DATA_PERIOD_MAP.get(interval)
    if thresholds is None:
        raise ValueError(f"Unsupported interval '{interval}'")
    for max_window, period in thresholds.items():
        if max_window is None or window <= max_window:
            return period


def get_stock_data(ticker: str, period: str = "1mo",
                   interval: str = "1d") -> yf.Ticker:
    """Fetch a yfinance Ticker object for the given symbol.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        period: History window (e.g. "1d", "1mo", "1y").
        interval: Bar size (e.g. "1d", "1wk", "1mo").

    Returns:
        A yfinance Ticker instance. Call `.history()` on it to
        retrieve a price DataFrame.

    Note:
        The returned object is the Ticker wrapper, not the
        DataFrame. This lets callers access info, financials,
        and other metadata beyond price history.
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    print(f"Fetched {len(hist)} rows for {ticker}")
    return stock


def calculate_sma(ticker: str, window: int,
                  interval: str = "1d") -> float:
    """Compute the latest simple moving average for a ticker.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Number of periods in the moving average.
        interval: Bar size ("1d", "1wk", "1mo").

    Returns:
        The most recent SMA value.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Note:
        The first `window - 1` rows of the rolling calculation
        are NaN and are discarded.
    """
    period = _data_period(window, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    sma = close.rolling(window=window).mean()
    value = sma.dropna().iloc[-1]
    print(f"{ticker} {window}-day SMA: {value:.2f}")
    return value


def calculate_ema(ticker: str, window: int,
                  interval: str = "1d") -> float:
    """Compute the latest exponential moving average for a ticker.

    Uses the standard span-based EMA (adjust=False) so the
    first observation is used as-is and subsequent values
    decay exponentially.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Span of the EMA (number of periods).
        interval: Bar size ("1d", "1wk", "1mo").

    Returns:
        The most recent EMA value.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    ema = close.ewm(span=window, adjust=False).mean()
    value = ema.dropna().iloc[-1]
    print(f"{ticker} {window}-day EMA: {value:.2f}")
    return value


def calculate_rsi(ticker: str, window: int,
                  interval: str = "1d") -> float:
    """Compute the latest Relative Strength Index for a ticker.

    Uses the standard Wilder smoothing method to normalise
    price momentum into a 0-100 range.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for averaging gains and losses.
        interval: Bar size ("1d", "1wk", "1mo").

    Returns:
        The most recent RSI value.

    Raises:
        IndexError: If insufficient data exists or all price
                    changes are zero (division by zero).

    Note:
        The first `window` rows of the RSI series are NaN and
        are discarded.
    """
    period = _data_period(window, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    delta = close.diff()              # period-over-period price changes
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss          # relative strength ratio
    rsi = 100.0 - (100.0 / (1.0 + rs))
    value = rsi.dropna().iloc[-1]
    print(f"{ticker} {window}-day RSI: {value:.2f}")
    return value


def main() -> None:
    """Parse user input and dispatch to the requested indicator.

    Expects three or four space-separated values: ticker, indicator
    name (SMA or RSI), lookback window, and optionally a bar size
    ("1d", "1wk", "1mo").  Defaults to "1d" if omitted.
    """
    user_input = input("Enter ticker, indicator (SMA/RSI), window"
                       " [and bar size (1d/1wk/1mo)]: ")
    parts = user_input.strip().split()

    if len(parts) < 3:                 # reject too few arguments
        print("Error: expected at least 3 values"
              " (ticker indicator window [bar_size])")
        sys.exit(1)

    ticker, indicator, period_str, *rest = parts
    interval = rest[0].lower() if rest else "1d"

    indicator = indicator.upper()
    if indicator not in ("SMA", "RSI", "EMA"):  # reject unknown indicator
        print("Error: indicator must be SMA or RSI")
        sys.exit(1)

    if interval not in _VALID_INTERVALS:  # reject unknown bar size
        print(f"Error: bar size must be one of"
              f" {', '.join(sorted(_VALID_INTERVALS))}")
        sys.exit(1)

    try:
        period = int(period_str)
    except ValueError:                 # reject non-numeric period
        print("Error: window must be an integer")
        sys.exit(1)
    if period <= 0:                    # reject non-positive period
        print("Error: window must be positive")
        sys.exit(1)

    match indicator:
        case "SMA":
            calculate_sma(ticker, period, interval=interval)
        case "EMA":
            calculate_ema(ticker, period, interval=interval)
        case "RSI":
            calculate_rsi(ticker, period, interval=interval)


if __name__ == "__main__":
    main()
