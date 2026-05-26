# indicators/sma.py
# Simple Moving Average (SMA) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_sma(ticker: str, window: int = 50,
                  interval: str = "1d",
                  count: int = 1,
                  _return_raw: bool = False
                  ) -> pd.Series | tuple[pd.Series, pd.Series]:
    """Compute the latest simple moving averages for a ticker.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Number of periods in the moving average.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent SMA values to return.
        _return_raw: If True, return (result, raw_close) tuple.

    Returns:
        A Series of the last `count` SMA values (single element
        when count=1).  When _return_raw is True, returns a
        (result, raw_close) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Note:
        The first `window - 1` rows of the rolling calculation
        are NaN and are discarded.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    sma = close.rolling(window=window).mean()
    result = sma.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for SMA({window}) with count={count}"
        )
    if _return_raw:
        return result, close
    return result
