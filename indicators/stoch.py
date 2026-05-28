# indicators/stoch.py
# Stochastic Oscillator (%K and %D lines) using SMA smoothing

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_stoch(ticker: str, window: int = 14,
                    smooth_k: int = 3, smooth_d: int = 3,
                    interval: str = "1d",
                    count: int = 1
                    ) -> tuple[pd.Series, pd.Series]:
    """Compute the latest Stochastic Oscillator values for a ticker.

    The Stochastic Oscillator compares each bar's close to the
    high-low range over a lookback window.  Raw %K is smoothed
    with an SMA to produce %K; %K is then smoothed with another
    SMA to produce %D (the signal line).

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for highest high / lowest low.
        smooth_k: SMA window applied to raw %K (default 3).
        smooth_d: SMA window applied to %K to produce %D
                  (default 3).
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent pairs to return.

    Returns:
        A tuple (%K, %D) of Series, each with the last `count`
        values (single elements when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    parameters.
    """
    period = _data_period(window + count + max(smooth_k, smooth_d),
                          interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    high = ohlcv["High"]
    low = ohlcv["Low"]
    close = ohlcv["Close"]

    highest_high = high.rolling(window=window).max()
    lowest_low = low.rolling(window=window).min()
    range_ = highest_high - lowest_low

    raw_k = 100.0 * (close - lowest_low) / range_
    k = raw_k.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()

    k_res = k.dropna().iloc[-count:]
    d_res = d.dropna().iloc[-count:]
    if k_res.empty or len(k_res) < count:
        raise IndexError(
            f"Insufficient data for STOCH({window},{smooth_k},"
            f"{smooth_d}) with count={count}"
        )
    return k_res, d_res
