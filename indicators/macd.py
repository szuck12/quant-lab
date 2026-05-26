# indicators/macd.py
# Moving Average Convergence Divergence (MACD) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_macd(ticker: str, fast: int = 12, slow: int = 26,
                   signal: int = 9, interval: str = "1d",
                   count: int = 1
                   ) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute MACD line, signal line, and histogram for a ticker.

    Uses the standard definition:
      MACD line   = EMA(fast) - EMA(slow)
      Signal line = EMA(MACD line, signal)
      Histogram   = MACD line - Signal line

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        fast: Fast EMA period.
        slow: Slow EMA period.
        signal: Signal EMA period.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent value-triplets to return.

    Returns:
        A tuple (macd_line, signal_line, histogram), each a
        Series of the last `count` values.

    Raises:
        IndexError: If insufficient data exists for the given
                    parameters.
    """
    period = _data_period(slow + signal + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    macd_line = (close.ewm(span=fast, adjust=False).mean()
                 - close.ewm(span=slow, adjust=False).mean())
    signal_line = macd_line.ewm(span=signal,
                                adjust=False).mean()
    histogram = macd_line - signal_line

    non_nan = ~(macd_line.isna() | signal_line.isna()
                | histogram.isna())
    macd_line = macd_line[non_nan].iloc[-count:]
    signal_line = signal_line[non_nan].iloc[-count:]
    histogram = histogram[non_nan].iloc[-count:]

    if len(macd_line) < count:
        raise IndexError(
            f"Insufficient data for MACD({fast},{slow},{signal})"
            f" with count={count}"
        )
    return macd_line, signal_line, histogram
