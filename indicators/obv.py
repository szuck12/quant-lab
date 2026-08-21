# indicators/obv.py
# On-Balance Volume (OBV) calculation function

import numpy as np
import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_obv(ticker: str, window: int = 30,
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest On-Balance Volume values for a ticker.

    OBV is a cumulative momentum indicator.  Each bar adds its
    volume to the running total when the close is above the
    previous close, subtracts it when below, and leaves the
    total unchanged when closes are equal:

        OBV_t = OBV_{t-1} + sign(C_t - C_{t-1}) * V_t

    The accumulation runs from the first fetched bar, so
    `window` controls how much history is included rather than
    a rolling calculation length.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Amount of history to fetch for the cumulative
                calculation.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent OBV values to return.

    Returns:
        A Series of the last `count` OBV values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists (fewer than two
                    bars).

    Note:
        The first bar has no previous close and produces NaN;
        accumulation starts from the second bar.
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    delta = ohlcv["Close"].diff()
    signed_volume = ohlcv["Volume"] * np.sign(delta)
    obv = signed_volume.cumsum()

    result = obv.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for OBV({window}) with count={count}"
        )
    return result
