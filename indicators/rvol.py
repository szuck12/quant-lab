# indicators/rvol.py
# Relative Volume (RVOL) calculation function

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_rvol(ticker: str, window: int = 10,
                   interval: str = "1d",
                   count: int = 1) -> pd.Series:
    """Compute the latest Relative Volume values for a ticker.

    RVOL = current Volume / rolling mean of Volume.  Values > 1.0
    indicate above-average volume, < 1.0 below-average volume.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent RVOL values to return.

    Returns:
        A Series of the last `count` RVOL values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window, or if all volume values are zero
                    (division by zero).

    Warning:
        All-zero volume over the window produces NaN (0/0) and
        raises IndexError, matching VWAP's behaviour.
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    volume = ohlcv["Volume"]
    av = volume.rolling(window=window).mean()
    rvol = volume / av
    result = rvol.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for RVOL({window}) with count={count}"
        )
    return result
