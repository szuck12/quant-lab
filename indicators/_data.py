# indicators/_data.py
# Shared data-fetching layer for all indicator functions

import re

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

_DEFAULT_WINDOWS: dict[str, int | tuple] = {
    "ADX": (14, 14),
    "ATR": 14,
    "AV": 20,
    "BB": (20, 2.0),
    "CCI": 20,
    "EMA": 20,
    "MACD": (12, 26, 9),
    "OBV": 30,
    "ROC": 9,
    "RSI": 14,
    "RVOL": 10,
    "SMA": 50,
    "STOCH": (14, 3, 3),
    "VWAP": 20,
}


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


_ANSI_ESCAPE_RE = re.compile(
    r"\x1b(?:"
    r"\[[0-9;:?]*[ -/]*[@-~]"      # CSI sequences (colours, etc)
    r"|[@-Z\-_]"                   # two-character escape sequences
    r"|\].*?(?:\x07|\x1b\\)"       # OSC sequences (title changes)
    r")"
)


def _sanitize_display(text: str) -> str:
    """Strip ANSI escape sequences and control characters.

    Prevents terminal escape-sequence injection through strings
    echoed from user input (e.g. colour codes embedded in a
    ticker symbol).  Complete escape sequences are removed first;
    any leftover non-printable characters are then dropped so
    output never alters terminal state.

    Args:
        text: Raw string that will be printed or logged.

    Returns:
        Text safe for terminal display.
    """
    cleaned = _ANSI_ESCAPE_RE.sub("", text)
    return "".join(ch for ch in cleaned if ch.isprintable())


def _fetch_close(ticker: str, period: str,
                 interval: str = "1d") -> pd.Series:
    """Fetch Close prices for a ticker and print the row count.

    Delegates to _fetch_ohlcv and extracts the Close column.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        period: History window (e.g. "1d", "1mo", "1y").
        interval: Bar size (e.g. "1d", "1wk", "1mo").

    Returns:
        A Series of Close prices indexed by date.
    """
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)
    if ohlcv.empty:
        return pd.Series(dtype=float)
    return ohlcv["Close"]


def _fetch_ohlcv(ticker: str, period: str,
                 interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data for a ticker and print the row count.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        period: History window (e.g. "1d", "1mo", "1y").
        interval: Bar size (e.g. "1d", "1wk", "1mo").

    Returns:
        A DataFrame with Open, High, Low, Close, Volume columns
        indexed by date. Returns an empty DataFrame if yfinance
        raises an exception (network error, invalid ticker,
        rate limit).
    """
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period=period, interval=interval)
    except Exception:
        print(f"Error: failed to fetch data for "
              f"{_sanitize_display(ticker)}")
        return pd.DataFrame()
    print(f"Fetched {len(hist)} rows for "
          f"{_sanitize_display(ticker)}")
    return hist
