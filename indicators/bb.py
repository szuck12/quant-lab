# indicators/bb.py
# Bollinger Bands (BB) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_bb(ticker: str, window: int = 20,
                 num_std: float = 2.0,
                 interval: str = "1d",
                 count: int = 1,
                 _return_raw: bool = False
                 ) -> tuple[pd.Series, pd.Series, pd.Series] \
                 | tuple[tuple[pd.Series, pd.Series, pd.Series],
                         pd.Series]:
    """Compute Bollinger Bands (upper, middle, lower) for a ticker.

    Middle band is an SMA of the close price.  Upper and lower
    bands are the middle band plus/minus ``num_std`` standard
    deviations (population std, ddof=0 — matching TradingView).

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Period for SMA and standard deviation.
        num_std: Number of standard deviations for band width.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent triplets to return.
        _return_raw: If True, return ((u,m,l), raw_close) tuple.

    Returns:
        A tuple (upper_band, middle_band, lower_band), each a
        Series of the last ``count`` values.  When _return_raw
        is True, returns a ((u,m,l), raw_close) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    parameters.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    middle = close.rolling(window=window).mean()
    std = close.rolling(window=window).std(ddof=0)
    upper = middle + num_std * std
    lower = middle - num_std * std

    non_nan = ~(upper.isna() | middle.isna() | lower.isna())
    upper = upper[non_nan].iloc[-count:]
    middle = middle[non_nan].iloc[-count:]
    lower = lower[non_nan].iloc[-count:]

    if len(upper) < count:
        raise IndexError(
            f"Insufficient data for BB({window},{num_std})"
            f" with count={count}"
        )
    if _return_raw:
        return (upper, middle, lower), close
    return upper, middle, lower
