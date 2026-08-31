# backtester/batch_indicators.py
"""Vectorized indicator computation on DataFrames.

Each function takes an OHLCV DataFrame and returns a Series or
tuple of Series. No yfinance calls — pure computation on
existing data. Mirrors the formulas in indicators/ but operates
on pre-fetched batch data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# -- Single-component indicators -----------------------------------------

def compute_sma(df: pd.DataFrame, window: int) -> pd.Series:
    """Simple Moving Average on Close.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period.

    Returns:
        SMA Series.
    """
    return df["Close"].rolling(window=window).mean()


def compute_ema(df: pd.DataFrame, window: int) -> pd.Series:
    """Exponential Moving Average on Close.

    Uses span-based EMA to match TradingView convention.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period (used as span).

    Returns:
        EMA Series.
    """
    return df["Close"].ewm(span=window, adjust=False).mean()


def compute_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Relative Strength Index with Wilder smoothing.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period (default 14).

    Returns:
        RSI Series (0-100).
    """
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1.0 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / window, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return rsi


def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range with Wilder smoothing.

    Args:
        df: OHLCV DataFrame with High, Low, Close columns.
        window: Lookback period (default 14).

    Returns:
        ATR Series.
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1.0 / window, adjust=False).mean()


def compute_cci(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Commodity Channel Index.

    Args:
        df: OHLCV DataFrame with High, Low, Close columns.
        window: Lookback period (default 20).

    Returns:
        CCI Series.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
    sma = typical.rolling(window=window).mean()
    mad = typical.rolling(window=window).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )
    cci = (typical - sma) / (0.015 * mad)
    return cci


def compute_obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume.

    Args:
        df: OHLCV DataFrame with Close and Volume columns.

    Returns:
        OBV Series.
    """
    direction = np.sign(df["Close"].diff())
    direction.iloc[0] = 0
    return (direction * df["Volume"]).cumsum()


def compute_roc(df: pd.DataFrame, window: int = 9) -> pd.Series:
    """Rate of Change.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period (default 9).

    Returns:
        ROC Series (percentage).
    """
    prev = df["Close"].shift(window)
    return (df["Close"] - prev) / prev * 100.0


def compute_rvol(df: pd.DataFrame, window: int = 10) -> pd.Series:
    """Relative Volume — current volume / average volume.

    Args:
        df: OHLCV DataFrame.
        window: Average volume lookback (default 10).

    Returns:
        RVOL Series.
    """
    avg_vol = df["Volume"].rolling(window=window).mean()
    return df["Volume"] / avg_vol


def compute_av(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Average Volume.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period (default 20).

    Returns:
        Average Volume Series.
    """
    return df["Volume"].rolling(window=window).mean()


def compute_vwap(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Volume-Weighted Average Price (rolling).

    Args:
        df: OHLCV DataFrame.
        window: Rolling window (default 20).

    Returns:
        VWAP Series.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3.0
    tp_vol = typical * df["Volume"]
    cum_tp_vol = tp_vol.rolling(window=window).sum()
    cum_vol = df["Volume"].rolling(window=window).sum()
    return cum_tp_vol / cum_vol


# -- Multi-component indicators ------------------------------------------

def compute_bb(
    df: pd.DataFrame, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands.

    Uses population standard deviation (ddof=0) to match
    TradingView.

    Args:
        df: OHLCV DataFrame.
        window: Lookback period (default 20).
        num_std: Standard deviation multiplier (default 2.0).

    Returns:
        (upper, middle, lower) Series tuple.
    """
    middle = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std(ddof=0)
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def compute_macd(
    df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD — Moving Average Convergence Divergence.

    Args:
        df: OHLCV DataFrame.
        fast: Fast EMA period (default 12).
        slow: Slow EMA period (default 26).
        signal: Signal line period (default 9).

    Returns:
        (macd_line, signal_line, histogram) Series tuple.
    """
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def compute_stoch(
    df: pd.DataFrame, window: int = 14, smooth_k: int = 3, smooth_d: int = 3
) -> tuple[pd.Series, pd.Series]:
    """Stochastic Oscillator.

    Args:
        df: OHLCV DataFrame with High, Low, Close columns.
        window: Lookback period (default 14).
        smooth_k: %K smoothing period (default 3).
        smooth_d: %D smoothing period (default 3).

    Returns:
        (k, d) Series tuple.
    """
    low_min = df["Low"].rolling(window=window).min()
    high_max = df["High"].rolling(window=window).max()
    raw_k = (df["Close"] - low_min) / (high_max - low_min) * 100.0
    k = raw_k.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()
    return k, d


def compute_adx(
    df: pd.DataFrame, di_len: int = 14, adx_len: int = 14
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Average Directional Index.

    Args:
        df: OHLCV DataFrame with High, Low, Close columns.
        di_len: DI smoothing period (default 14).
        adx_len: ADX smoothing period (default 14).

    Returns:
        (plus_di, minus_di, adx) Series tuple.
    """
    high = df["High"]
    low = df["Low"]

    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=df.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=df.index,
    )

    atr = compute_atr(df, window=di_len)

    smooth_plus = plus_dm.ewm(alpha=1.0 / di_len, adjust=False).mean()
    smooth_minus = minus_dm.ewm(alpha=1.0 / di_len, adjust=False).mean()

    plus_di = 100.0 * smooth_plus / atr
    minus_di = 100.0 * smooth_minus / atr

    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=1.0 / adx_len, adjust=False).mean()

    return plus_di, minus_di, adx


# -- Component dispatch table --------------------------------------------

INDICATORS: dict[str, str] = {
    "ADX": "adx",
    "ATR": "atr",
    "AV": "av",
    "BB": "bb",
    "CCI": "cci",
    "EMA": "ema",
    "MACD": "macd",
    "OBV": "obv",
    "ROC": "roc",
    "RSI": "rsi",
    "RVOL": "rvol",
    "SMA": "sma",
    "STOCH": "stoch",
    "VWAP": "vwap",
}

COMPONENT_MAP: dict[str, list[str]] = {
    "ADX": ["plus_di", "minus_di", "adx"],
    "ATR": ["value"],
    "AV": ["value"],
    "BB": ["upper", "middle", "lower"],
    "CCI": ["value"],
    "EMA": ["value"],
    "MACD": ["line", "signal", "hist"],
    "OBV": ["value"],
    "ROC": ["value"],
    "RSI": ["value"],
    "RVOL": ["value"],
    "SMA": ["value"],
    "STOCH": ["k", "d"],
    "VWAP": ["value"],
}


def compute_indicator(
    df: pd.DataFrame,
    indicator: str,
    params: tuple,
    component: str | None = None,
) -> pd.Series:
    """Compute an indicator on a DataFrame.

    Dispatches to the correct batch computation function.

    Args:
        df: OHLCV DataFrame.
        indicator: Indicator name (e.g. "RSI", "BB").
        params: Indicator parameters as a tuple.
        component: For multi-component indicators, which
            component to return (e.g. "upper" for BB).
            None returns the default (value for single-component,
            first component for multi-component).

    Returns:
        Computed indicator as a Series.

    Raises:
        ValueError: If indicator or component is unknown.
    """
    ind = indicator.upper()
    if ind not in INDICATORS:
        raise ValueError(f"Unknown indicator '{ind}'")

    valid_components = COMPONENT_MAP[ind]
    if component and component not in valid_components:
        raise ValueError(
            f"Indicator {ind} has no component '{component}'. "
            f"Valid: {', '.join(sorted(valid_components))}"
        )

    # Convert whole-number float params to int (e.g. 50.0 → 50).
    # CLI parser stores all params as float; pandas rolling() and
    # other APIs require int windows. Defense in depth: the CLI
    # parser also converts, but this catches any direct caller.
    params = tuple(
        int(p) if isinstance(p, float) and p == int(p) else p
        for p in params
    )

    if ind == "SMA":
        result = compute_sma(df, *params)
    elif ind == "EMA":
        result = compute_ema(df, *params)
    elif ind == "RSI":
        result = compute_rsi(df, *params)
    elif ind == "ATR":
        result = compute_atr(df, *params)
    elif ind == "CCI":
        result = compute_cci(df, *params)
    elif ind == "OBV":
        result = compute_obv(df)
    elif ind == "ROC":
        result = compute_roc(df, *params)
    elif ind == "RVOL":
        result = compute_rvol(df, *params)
    elif ind == "AV":
        result = compute_av(df, *params)
    elif ind == "VWAP":
        result = compute_vwap(df, *params)
    elif ind == "BB":
        upper, middle, lower = compute_bb(df, *params)
        mapping = {"upper": upper, "middle": middle, "lower": lower}
        result = mapping.get(component, middle)
    elif ind == "MACD":
        line, signal, hist = compute_macd(df, *params)
        mapping = {"line": line, "signal": signal, "hist": hist}
        result = mapping.get(component, line)
    elif ind == "STOCH":
        k, d = compute_stoch(df, *params)
        mapping = {"k": k, "d": d}
        result = mapping.get(component, k)
    elif ind == "ADX":
        plus_di, minus_di, adx = compute_adx(df, *params)
        mapping = {"plus_di": plus_di, "minus_di": minus_di, "adx": adx}
        result = mapping.get(component, adx)
    else:
        raise ValueError(f"Indicator '{ind}' not implemented")

    return result
