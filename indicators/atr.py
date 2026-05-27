# indicators/atr.py
# Average True Range (ATR) calculation function

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_atr(ticker: str, window: int = 14,
                  interval: str = "1d",
                  count: int = 1,
                  _return_raw: bool = False
                  ) -> pd.Series | tuple[pd.Series, pd.Series]:
    """Compute the latest Average True Range values for a ticker.

    True Range (TR) is the greatest of three gaps on each bar:
      high - low, |high - prev_close|, |low - prev_close|

    ATR is the Wilder-smoothed (RMA) average of TR over the given
    window, matching TradingView's default ATR calculation.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for Wilder smoothing.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent ATR values to return.
        _return_raw: If True, return (result, tr) tuple where tr
                     is the raw True Range series.

    Returns:
        A Series of the last `count` ATR values (single element
        when count=1).  When _return_raw is True, returns a
        (result, tr) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Note:
        The first TR value is always NaN (no previous close from
        which to compute the gap).  Wilder smoothing produces NaN
        until the seed period is complete, so ATR has at least
        one NaN row even after dropping TR's initial NaN.
    """
    period = _data_period(window + count, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    prev_close = ohlcv["Close"].shift(1)
    high_low = ohlcv["High"] - ohlcv["Low"]
    high_pc = (ohlcv["High"] - prev_close).abs()
    low_pc = (ohlcv["Low"] - prev_close).abs()

    tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / window, adjust=False).mean()

    result = atr.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for ATR({window}) with count={count}"
        )
    if _return_raw:
        return result, tr
    return result
