# Commenting Guidelines

## 1. Module / File Headers

Every `.py` file starts with a brief comment describing the module's purpose.

```python
# init.py
# yfinance API connection and data fetching utilities
```

## 2. Google-Style Docstrings

All public functions, methods, and classes must have a docstring following the Google style.

```python
def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    """Fetch historical price data for a given ticker.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        period: Time period (e.g. "1d", "1mo", "1y").

    Returns:
        DataFrame with OHLCV columns indexed by date.

    Raises:
        ValueError: If ticker is empty or invalid.
    """
```

- Always include `Args:`, `Returns:`, and `Raises:` when applicable.
- Describe the *what* and *why*, not the implementation detail.

### Attributes

Include an `Attributes:` section in class docstrings for all instance variables.

```python
class SMAIndicator:
    """Computes simple moving averages.

    Attributes:
        window: Lookback period for the SMA.
        data: Input price series.
    """
```

## 3. Type Hints

Annotate every function signature with type hints. This reduces the need for inline comments about expected types.

```python
def calculate_sma(data: pd.Series, window: int = 20) -> pd.Series:
```

## 4. Inline Comments

Use inline comments sparingly. When used, they must explain *why*, not *what*.
For complex blocks of code, inline comments can be used sparingly to describe
what the code is doing.

```python
# Good — explains the reasoning
sma = data.rolling(window).mean()  # 20-period SMA smoothes short-term noise

# Good — describes complex logic
delta = close.diff()              # period-over-period price changes
gain = delta.where(delta > 0, 0.0)

# Bad — states the obvious
sma = data.rolling(window).mean()  # calculate rolling mean
```

## 5. Block Comments

For multi-step algorithms or complex indicator logic, use block comments above the code block.

```python
# -------------------------------------------------------------------
# RSI Calculation
# 1. Compute daily price changes
# 2. Separate gains and losses
# 3. Average gain / loss over the lookback window
# 4. Normalize to 0-100 range
# -------------------------------------------------------------------
```

## 6. TODO / FIXME Markers

Standardize markers for incomplete or flagged code.

```python
# TODO(username): implement variance thresholding logic
# FIXME: division by zero occurs when volume is 0 for the period
```

## 7. Deprecation Annotation

Mark deprecated functions with a `Deprecated:` section in the docstring and a `warnings.warn` call.

```python
import warnings


def old_function() -> None:
    """Do something the old way.

    Deprecated:
        Use `new_function()` instead. Will be removed in v2.0.
    """
    warnings.warn("old_function is deprecated, use new_function", DeprecationWarning, stacklevel=2)
```

## 8. Line Length / Formatting

Restrict all comments, docstrings, and code to **80 characters maximum**.

- Break long inline comments onto a separate line above the code.
- Wrap docstring lines to stay under the limit.
- Use parentheses or backslashes for implicit line continuation when needed.

```python
# Good — broken before 80 chars
sma = data.rolling(window=20).mean()
# This is a longer inline comment that would exceed 80 characters so it goes
# on its own line above the code instead.

# Bad — exceeds limit
sma = data.rolling(window=20).mean()  # this comment goes way past 80 characters and should be broken up
```

## 9. Note / Warning Callouts

Use `Note:` and `Warning:` in docstrings to flag edge cases or important caveats.

```python
def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Compute Relative Strength Index.

    Note:
        The first `window` rows will be NaN since there is
        insufficient data to compute the initial RSI.

    Warning:
        A period of all-zero price changes will produce a
        division-by-zero result. Callers should handle this case.
    """
```

## 10. What NOT to Comment

- Self-documenting code (e.g. `total = price * quantity  # calculate total`)
- Obvious control flow (e.g. `i += 1  # increment i`)
- Type information already covered by type hints

## 11. Vertical Spacing

Use blank lines to separate logical sections for readability.

- **Two blank lines** between top-level definitions (functions,
  classes) — standard PEP 8.
- **One blank line** between import groups (stdlib, third-party,
  local).
- **One blank line** between separate logical phases within a
  function or `__main__` block (e.g. input, validation, dispatch).

```python
def calculate_rsi(ticker: str, window: int) -> float:
    """Compute the latest Relative Strength Index for a ticker."""
    stock = get_stock_data(ticker, period="max")
    close = stock.history(period="max")["Close"]

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.dropna().iloc[-1]
```


