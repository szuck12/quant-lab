# indicators/roc.py
# Rate of Change (ROC) calculation function

import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_roc(ticker: str, window: int = 9,
                  interval: str = "1d",
                  count: int = 1) -> pd.Series:
    """Compute the latest Rate of Change values for a ticker.

    ROC measures the percentage change of the close price over
    the last `window` bars:

        ROC = (close - close[window bars ago])
              / close[window bars ago] * 100

    Positive values indicate upward momentum, negative values
    downward momentum.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent ROC values to return.

    Returns:
        A Series of the last `count` ROC values (single element
        when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window.

    Warning:
        A close price of exactly zero `window` bars ago makes
        ROC undefined; those rows are dropped like NaN rows and
        count against data sufficiency.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    prior = close.shift(window)
    roc = (close - prior) / prior * 100
    # A zero price `window` bars ago yields +/-inf, which is not
    # an interpretable momentum value -- treat it like NaN so it
    # is discarded with the other leading-edge rows.
    roc = roc.replace([float("inf"), float("-inf")], float("nan"))

    result = roc.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for ROC({window}) with count={count}"
        )
    return result
