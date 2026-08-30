---
name: add-indicator-implement
description: Code patterns for implementing a new indicator. Loaded by the Feature Implementer during the add-indicator workflow.
---

# Implement New Indicator — Code Patterns

## Overview

This file contains the exact code patterns for implementing a new
indicator. Referenced by `skills/add-indicator/SKILL.md` Step 3.

## 1. Implementation File

Create `indicators/<name>.py`:

```python
# indicators/<name>.py
"""<Indicator full name> calculation."""


def calculate_<indicator>(ticker: str, window: int,
                          interval: str = "1d",
                          count: int = 1
                          ) -> pd.Series:
    """Compute the latest <full name> values for a ticker.

    <One-paragraph description>.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent values to return.

    Returns:
        A Series of the last `count` <indicator> values.

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period,
                         interval=interval)
    # ... calculation ...
    result = <series>.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for <INDICATOR>({window})"
            f" with count={count}"
        )
    return result
```

### Multi-Param Variant

For indicators with extra parameters (e.g. MACD, BB, STOCH, ADX):

```python
def calculate_macd(ticker: str, fast: int, slow: int,
                   signal: int, interval: str = "1d",
                   count: int = 1
                   ) -> tuple[pd.Series, pd.Series,
                              pd.Series]:
```

Extra params come between `window` (or named params) and `interval`.

## 2. Registration (4 Locations)

### `indicators/__init__.py`

Add import in alphabetical position:

```python
from indicators.<name> import calculate_<name>
```

### `main.py` — Import

Add import in alphabetical position among indicator imports.

### `main.py` — Prompt String

Add indicator name to the input prompt list in alphabetical position.

### `main.py` — Validation Set

Add the indicator's uppercase name to the validation set in
alphabetical position.

### `main.py` — Dispatch

Add `case` block in alphabetical position:

```python
case "<INDICATOR>":
    result = calculate_<indicator>(
        ticker, window, interval=interval, count=count)
```

### `indicators/_data.py` — Default Windows

Add entry to `_DEFAULT_WINDOWS` in alphabetical position:

```python
"<INDICATOR>": <default_window>,  # single-param
"<INDICATOR>": (12, 26, 9),       # multi-param
```

## 3. Pre-Handoff Checks

```bash
ruff check main.py indicators/<name>.py
echo "AAPL <INDICATOR> <default_window>" | python3 main.py
```

Both must pass before handing to the Test Engineer.
