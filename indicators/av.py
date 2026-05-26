# indicators/av.py
# Average Volume (AV) calculation function

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_av(ticker: str, window: int = 20,
                 interval: str = "1d",
                 count: int = 1,
                 _return_raw: bool = False
                 ) -> pd.Series | tuple[pd.Series, pd.Series]:
    """Compute the latest Average Volume values for a ticker.

    Simple rolling mean of Volume over the given window, matching
    the SMA pattern applied to volume data.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent AV values to return.
        _return_raw: If True, return (result, raw_volume) tuple.

    Returns:
        A Series of the last `count` AV values (single element
        when count=1).  When _return_raw is True, returns a
        (result, raw_volume) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Note:
        Zero-volume periods produce AV=0.0, which is a valid
        result (unlike VWAP which would divide by zero).
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    av = ohlcv["Volume"].rolling(window=window).mean()
    result = av.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for AV({window}) with count={count}"
        )
    if _return_raw:
        return result, ohlcv["Volume"]
    return result
