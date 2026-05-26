# indicators/rsi.py
# Relative Strength Index (RSI) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_rsi(ticker: str, window: int = 14,
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
    close = _fetch_close(ticker, period=period, interval=interval)

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
