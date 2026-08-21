# indicators/adx.py
# Average Directional Index (+DI, -DI, ADX) using Wilder smoothing

import pandas as pd

from indicators._data import _fetch_ohlcv, _data_period


def calculate_adx(ticker: str, window: int = 14,
                  adx_window: int = 14,
                  interval: str = "1d",
                  count: int = 1
                  ) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute the latest +DI, -DI, and ADX values for a ticker.

    Implements Wilder's Directional Movement system.  Upward and
    downward movement are extracted from consecutive highs and
    lows, smoothed with Wilder's RMA (alpha = 1 / window), and
    normalised by the smoothed True Range to produce +DI and
    -DI.  ADX is the RMA of the DX ratio over `adx_window` and
    measures trend strength regardless of direction.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period for the DI smoothing.
        adx_window: Smoothing period applied to DX to produce
                    ADX.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent values to return.

    Returns:
        A tuple (plus_di, minus_di, adx) of Series, each with
        the last `count` values (single elements when count=1).

    Raises:
        IndexError: If insufficient data exists (fewer than two
                    bars) or zero denominators leave no valid
                    values.

    Note:
        The first bar has no previous bar, so directional
        movement is NaN there.  DX is NaN whenever +DI + -DI is
        zero; those rows are dropped like other NaN rows.
    """
    period = _data_period(window + count + adx_window, interval)
    ohlcv = _fetch_ohlcv(ticker, period=period, interval=interval)

    high = ohlcv["High"]
    low = ohlcv["Low"]
    close = ohlcv["Close"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0),
                            0.0)
    minus_dm = down_move.where((down_move > up_move)
                               & (down_move > 0), 0.0)
    plus_dm = plus_dm.mask(up_move.isna())
    minus_dm = minus_dm.mask(up_move.isna())

    prev_close = close.shift(1)
    tr = pd.concat([high - low,
                    (high - prev_close).abs(),
                    (low - prev_close).abs()],
                   axis=1).max(axis=1)

    alpha = 1.0 / window
    atr = tr.ewm(alpha=alpha, adjust=False).mean()
    plus_di = 100.0 * plus_dm.ewm(alpha=alpha,
                                  adjust=False).mean() / atr
    minus_di = 100.0 * minus_dm.ewm(alpha=alpha,
                                    adjust=False).mean() / atr

    di_sum = plus_di + minus_di
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    adx = dx.ewm(alpha=1.0 / adx_window, adjust=False).mean()

    p_res = plus_di.dropna().iloc[-count:]
    m_res = minus_di.dropna().iloc[-count:]
    a_res = adx.dropna().iloc[-count:]
    if (p_res.empty or len(p_res) < count
            or m_res.empty or len(m_res) < count
            or a_res.empty or len(a_res) < count):
        raise IndexError(
            f"Insufficient data for ADX({window},{adx_window})"
            f" with count={count}"
        )
    return p_res, m_res, a_res
