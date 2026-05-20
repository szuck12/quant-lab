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

_DEFAULT_WINDOWS: dict[str, int] = {
    "SMA": 50,
    "EMA": 20,
    "RSI": 14,
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
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest simple moving averages for a ticker.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Number of periods in the moving average.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent SMA values to return.

    Returns:
        A Series of the last `count` SMA values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Note:
        The first `window - 1` rows of the rolling calculation
        are NaN and are discarded.
    """
    period = _data_period(window + count, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    sma = close.rolling(window=window).mean()
    result = sma.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for SMA({window}) with count={count}"
        )
    return result


def calculate_ema(ticker: str, window: int,
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest exponential moving averages for a ticker.

    Uses the standard span-based EMA (adjust=False) so the
    first observation is used as-is and subsequent values
    decay exponentially.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Span of the EMA (number of periods).
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent EMA values to return.

    Returns:
        A Series of the last `count` EMA values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window + count, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    ema = close.ewm(span=window, adjust=False).mean()
    result = ema.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for EMA({window}) with count={count}"
        )
    return result


def calculate_rsi(ticker: str, window: int,
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest Relative Strength Index values for a ticker.

    Uses Wilder smoothing (RMA) to normalise price momentum into a
    0-100 range, matching TradingView's default RSI calculation.
    The first non-NaN value appears after one price change.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for averaging gains and losses.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent RSI values to return.

    Returns:
        A Series of the last `count` RSI values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists or all price
                    changes are zero (division by zero).

    Note:
        With Wilder smoothing the first row is always NaN
        (division of zero by zero from the initial seed).
        All subsequent values are valid after at least one
        price change.
    """
    period = _data_period(window + count, interval)
    stock = get_stock_data(ticker, period=period, interval=interval)
    close = stock.history(period=period, interval=interval)["Close"]

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    result = rsi.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for RSI({window}) with count={count}"
        )
    return result


def main() -> None:
    """Parse user input and dispatch to the requested indicator.

    Expects at least two space-separated values: ticker and indicator
    name (SMA, RSI, or EMA).  Optional trailing arguments can appear
    in any order:

      * A recognised bar size sets the interval ("1d", "1wk", "1mo").
      * A plain positive integer sets the lookback window.
      * "C" followed by a positive integer (e.g. "C10") sets the
        number of most-recent indicator values to return.

    Defaults are "1d" for interval, indicator-specific windows
    (SMA=50, EMA=20, RSI=14), and count=1.
    """
    user_input = input("Enter ticker, indicator (SMA/RSI/EMA)"
                       " [bar_size] [window] [C<count>]: ")
    parts = user_input.strip().split()

    if len(parts) < 2:
        print("Error: expected at least 2 values"
              " (ticker indicator [bar_size] [window] [C<count>])")
        sys.exit(1)

    ticker, indicator, *rest = parts
    indicator = indicator.upper()
    if indicator not in ("SMA", "RSI", "EMA"):
        print("Error: indicator must be SMA, RSI, or EMA")
        sys.exit(1)

    interval = "1d"
    window = _DEFAULT_WINDOWS[indicator]
    count = 1
    seen_interval = False
    seen_window = False
    seen_count = False

    for arg in rest:
        lowered = arg.lower()
        if lowered in _VALID_INTERVALS:
            if seen_interval:
                print(f"Error: duplicate bar size '{arg}'")
                sys.exit(1)
            interval = lowered
            seen_interval = True
        elif lowered.startswith("c"):
            if seen_count:
                print(f"Error: duplicate count '{arg}'")
                sys.exit(1)
            try:
                count = int(lowered[1:])
            except ValueError:
                print(f"Error: invalid count '{arg}'"
                      " (use C<number>, e.g. C10)")
                sys.exit(1)
            if count <= 0:
                print("Error: count must be positive")
                sys.exit(1)
            seen_count = True
        else:
            try:
                w = int(arg)
            except ValueError:
                print(f"Error: unrecognised argument '{arg}'")
                sys.exit(1)
            if w <= 0:
                print("Error: window must be positive")
                sys.exit(1)
            if seen_window:
                print(f"Error: duplicate window '{arg}'")
                sys.exit(1)
            window = w
            seen_window = True

    match indicator:
        case "SMA":
            result = calculate_sma(ticker, window,
                                   interval=interval, count=count)
        case "EMA":
            result = calculate_ema(ticker, window,
                                   interval=interval, count=count)
        case "RSI":
            result = calculate_rsi(ticker, window,
                                   interval=interval, count=count)

    if count == 1:
        print(f"{ticker} {window}-{indicator}: {result.iloc[-1]:.2f}")
    else:
        print(f"{ticker} {window}-{indicator} (last {count}):")
        for val in result:
            print(f"  {val:.2f}")


if __name__ == "__main__":
    main()
