# indicators/ema.py
# Exponential Moving Average (EMA) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_ema(ticker: str, window: int = 20,
                  interval: str = "1d",
                  count: int = 1,
                  _return_raw: bool = False
                  ) -> pd.Series | tuple[pd.Series, pd.Series]:
    """Compute the latest exponential moving averages for a ticker.

    Uses the standard span-based EMA (adjust=False) so the
    first observation is used as-is and subsequent values
    decay exponentially.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Span of the EMA (number of periods).
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent EMA values to return.
        _return_raw: If True, return (result, raw_close) tuple.

    Returns:
        A Series of the last `count` EMA values (single element
        when count=1).  When _return_raw is True, returns a
        (result, raw_close) tuple.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    ema = close.ewm(span=window, adjust=False).mean()
    result = ema.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for EMA({window}) with count={count}"
        )
    if _return_raw:
        return result, close
    return result
