# indicators/cci.py
# Commodity Channel Index (CCI) calculation function

import numpy as np
import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_cci(ticker: str, window: int = 20,
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest Commodity Channel Index values for a
    ticker.

    CCI compares the Typical Price (High + Low + Close) / 3 to
    its Simple Moving Average over the window, normalised by
    0.015 times the Mean Deviation — the average absolute
    distance between each Typical Price in the window and that
    window's SMA.  Unlike most oscillators, CCI is unbounded;
    values beyond +/-100 indicate unusually strong deviation.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for the SMA and Mean Deviation.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent CCI values to return.

    Returns:
        A Series of the last `count` CCI values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window or no valid values remain after
                    dropping NaN rows.

    Note:
        The first window - 1 bars produce NaN (rolling
        semantics).  A zero Mean Deviation (e.g. constant
        prices) divides zero by zero and produces NaN; those
        rows are dropped like other NaN rows.
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    typical = (ohlcv["High"] + ohlcv["Low"]
               + ohlcv["Close"]) / 3.0
    sma = typical.rolling(window=window).mean()
    mean_dev = typical.rolling(window=window).apply(
        lambda values: np.abs(values - values.mean()).mean(),
        raw=True
    )
    cci = (typical - sma) / (0.015 * mean_dev)

    result = cci.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for CCI({window}) with count={count}"
        )
    return result
