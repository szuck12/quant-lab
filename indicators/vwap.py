# indicators/vwap.py
# Volume-Weighted Average Price (VWAP) calculation function

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_vwap(ticker: str, window: int = 20,
                   interval: str = "1d",
                   count: int = 1,
                   _return_raw: bool = False
                   ) -> pd.Series | tuple[pd.Series, pd.Series]:
    """Compute the latest Volume Weighted Average Price for a
    ticker.

    Uses the standard definition:
      Typical Price = (High + Low + Close) / 3
      VWAP = sum(TP * Volume) over window
             / sum(Volume) over window

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent VWAP values to return.
        _return_raw: If True, return (result, typical) tuple.

    Returns:
        A Series of the last `count` VWAP values (single element
        when count=1).  When _return_raw is True, returns a
        (result, typical) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    typical = (ohlcv["High"] + ohlcv["Low"] + ohlcv["Close"]) / 3.0
    pv = typical * ohlcv["Volume"]
    cum_pv = pv.rolling(window=window).sum()
    cum_v = ohlcv["Volume"].rolling(window=window).sum()
    vwap = cum_pv / cum_v

    result = vwap.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for VWAP({window}) with count={count}"
        )
    if _return_raw:
        return result, typical
    return result
