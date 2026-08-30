# Adding a New Indicator

This document describes the process for adding a new technical indicator to
QuantLab. Follow these steps in order. Each step references the
existing indicator implementations as templates (e.g. ATR for Wilder-smoothing / OHLCV, AV or SMA for simple rolling windows).

## Agent Workflow

Adding an indicator is a multi-agent task routed by the Task Orchestrator and
executed by the specialists named at each step below. The chain is:

```
indicator-specialist → feature-implementer ⇄ data-engineer → test-engineer
  → consistency-guardian → documentation-expert → code-reviewer
  + security-auditor → release-manager
```

See `docs/agent_workflows.md` (Workflow A) and `AGENTS.md` for the full model.

## 0. Create a TODO Entry

*(Agent: Idea Generator to triage; Task Orchestrator to schedule;
Documentation Expert to draft the entry.)*

Before implementing, add a TODO item to `TODO.md` (see
[docs/maintain_todo.md](maintain_todo.md)).  Determine the priority based on
how important the change is — requested changes are not automatically high
priority.  Use an unchecked box (`[ ]`) and move the item to **In Progress**
once you start implementation.

## 1. Information to Gather

*(Agent: Indicator Specialist.)*

Before writing code, clarify these points with the person requesting
the indicator:

- **Name and abbreviation.** Ask if not provided in the request
  (e.g. "MACD", "BB", "VWAP").

- **Formula.** Rather than asking for the definition, offer the most
  common implementation for the requested indicator. If multiple
  common variants exist, list them and let the user choose. If none
  fit, the user can describe their exact formula.

  Examples of what to offer:
  - MACD: standard EMA(12) - EMA(26) with 9-period signal line
  - Bollinger Bands: 20-period SMA with +/-2 standard deviations
  - VWAP: cumulative (price * volume) / cumulative volume

- **Default window.** Offer the most common default for that
  indicator (e.g. TradingView's default), rather than asking
  open-ended. The user can accept or override it.

- **Data requirements.** Inferred from the formula -- confirm with
  the user (e.g. "VWAP needs both Close and Volume -- is yfinance
  providing that?" or "This only uses Close, correct?").

- **Edge cases.** Derived from the formula during implementation.
  Flag any obvious boundary conditions (division by zero, constant
  prices, NaN handling) and ask for clarification only when the
  correct behaviour is ambiguous.

- **Reference values.** Compute a known-answer test from the
  formula implementation. If the user has a specific TradingView
  or other reference they want matched exactly, they can provide
  it -- no need to ask proactively.

## 2. Implementation in `indicators/` subpackage

*(Agent: Feature Implementer; the data-layer changes in 2a/2d are owned
by the Data Engineer.)*

### 2a. Create `indicators/<name>.py`

Create a new file `indicators/<name>.py` following the same signature
pattern as the existing indicators.  Import data helpers from
`indicators._data`:

```python
import pandas as pd

from indicators._data import _fetch_close, _data_period


def calculate_<indicator>(ticker: str, window: int,
                          interval: str = "1d",
                          count: int = 1
                          ) -> pd.Series:
    """Compute the latest <full name> values for a ticker.

    <One-paragraph description of the calculation>.

    Args:
        ticker: Stock symbol (e.g. "AAPL").
        window: Lookback period in bars.
        interval: Bar size ("1d", "1wk", "1mo").
        count: Number of most recent values to return.

    Returns:
        A Series of the last `count` <indicator> values (single
        element when count=1).

    Raises:
        IndexError: If insufficient data exists for the given
                    window.
    """
    period = _data_period(window + count, interval)
    close = _fetch_close(ticker, period=period, interval=interval)

    # ... indicator calculation ...

    result = <series>.dropna().iloc[-count:]
    if result.empty or len(result) < count:
        raise IndexError(
            f"Insufficient data for <INDICATOR>({window})"
            f" with count={count}"
        )
    return result
```

If the indicator needs OHLCV data (Open, High, Low, Close, Volume) instead
of just Close, import `_fetch_ohlcv` instead:

```python
from indicators._data import _fetch_ohlcv, _data_period
```

### 2b. Re-export in `indicators/__init__.py`

Add an import line to `indicators/__init__.py`:

```python
from indicators.<name> import calculate_<indicator>
```

### 2c. Re-export in `main.py`

Add an import line to `main.py` so that `from main import calculate_<indicator>`
still works for any external consumers:

```python
from indicators import calculate_sma, ..., calculate_<indicator>
```

Maintain alphabetical order in the import list.

### 2d. Add a default window (if applicable)

If the indicator has a sensible default window, add one entry to the
`_DEFAULT_WINDOWS` dictionary in `indicators/_data.py` in
alphabetical position:

```python
_DEFAULT_WINDOWS: dict[str, int | tuple] = {
    "ADX": (14, 14),
    "ATR": 14,
    "AV": 20,
    "BB": (20, 2.0),
    ...
    "<INDICATOR>": <default_window>,
    ...
}
```

### 2e. Register the indicator in `main()`

Three changes inside `main()` in `main.py`:

1. **Prompt** — add the new indicator name to the list shown to the user
   in the `input()` call, maintaining alphabetical order:
   ```python
   user_input = input("Enter ticker(s), indicator"
                      " (ADX/ATR/AV/BB/CCI/EMA/MACD/OBV/"
                      "ROC/RSI/RVOL/SMA/STOCH/VWAP/<INDICATOR>)"
                      " [bar_size] [window] [C<count>]: ")
   ```

2. **Validation set** — add the uppercased name to the
   `indicator.upper()` check, maintaining alphabetical order:
   ```python
   indicator = indicator.upper()
   if indicator not in ("ADX", "ATR", "AV", "BB", "CCI", "EMA",
                        "MACD", "OBV", "ROC", "RSI", "RVOL",
                        "SMA", "STOCH", "VWAP", "<INDICATOR>"):
   ```

3. **Dispatch match/case** — add a new case block inside the
   `match indicator:` block, in alphabetical position:
   ```python
   case "<INDICATOR>":
       result = calculate_<indicator>(ticker, window,
                                      interval=interval,
                                      count=count)
   ```

### 2f. Follow the commenting guidelines

Follow the [commenting guidelines](commenting_guidelines.md) for docstring
style, type hints, inline comments, and line length.

## 3. Mock Tests

*(Agent: Test Engineer; reference values supplied by the Indicator
Specialist.)*

### 3a. Create `mocktests/test_calculate_<indicator>.py`

Create a new file using the `mock_stock_data` fixture from
`mocktests/conftest.py`. The fixture accepts a list of Close prices and
patches `yf.Ticker` to return them. The mock ignores the period and
interval parameters, so interval-specific tests (weekly, monthly) are
not useful -- they test the same code path as the default interval.

Include tests from each category below. Data sizes range from 0 to 20
entries for comprehensive coverage.

**Reference test** (1 test -- known answer for a specific algorithm):

```python
def test_basic_<indicator>(self, mock_stock_data):
    """Verify <indicator> matches the known value for a small
    price sequence."""
    mock_stock_data([10, 11, 12, 13, 14, 15])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == pytest.approx(<expected>, abs=0.0001)
```

**Window edge tests** (3-4 tests -- boundary conditions on window size):

```python
def test_window_one(self, mock_stock_data):
    """Verify <indicator> with window=1 equals the last close."""
    mock_stock_data([10, 20])
    result = calculate_<indicator>("TEST", 1)
    assert result.iloc[-1] == 20.0

def test_window_exceeds_data(self, mock_stock_data):
    """Verify behaviour when window is larger than the data
    set.  SMA-based indicators raise IndexError; EMA/RSI
    still produce a result."""
    mock_stock_data([1, 2, 3])
    with pytest.raises(IndexError):
        calculate_<indicator>("TEST", 10)

def test_insufficient_data(self, mock_stock_data):
    """Verify IndexError is raised with no data."""
    mock_stock_data([])
    with pytest.raises(IndexError):
        calculate_<indicator>("TEST", 5)
```

Note: `test_window_exceeds_data` raises IndexError for SMA (rolling
produces all NaN) but not for EMA/RSI. Adjust the assertion based on
the indicator's behaviour.

**Data pattern tests** (4-5 tests -- challenging input shapes):

```python
def test_constant_prices(self, mock_stock_data):
    """Verify <indicator> handles all-identical prices."""
    mock_stock_data([50, 50, 50, 50, 50, 50])
    result = calculate_<indicator>("TEST", 2)
    assert result.iloc[-1] == pytest.approx(50.0, abs=0.0001)

def test_alternating_pattern(self, mock_stock_data):
    """Verify <indicator> handles a zigzag price pattern."""
    mock_stock_data([10, 20, 10, 20, 10, 20, 10, 20])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == pytest.approx(<expected>, abs=0.01)

def test_large_prices(self, mock_stock_data):
    """Verify <indicator> handles prices around 1e9."""
    mock_stock_data([1e9, 1.001e9, 1.002e9, 1.003e9,
                     1.004e9])
    result = calculate_<indicator>("TEST", 2)
    assert result.iloc[-1] == pytest.approx(<expected>, rel=1e-6)

def test_negative_prices(self, mock_stock_data):
    """Verify <indicator> handles negative prices."""
    mock_stock_data([-10, -9, -8, -7, -6, -5, -4])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == pytest.approx(<expected>, abs=0.0001)

def test_spike_pattern(self, mock_stock_data):
    """Verify <indicator> handles one spike in a flat series."""
    mock_stock_data([10, 10, 10, 10, 1000, 10, 10, 10, 10,
                     10])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == pytest.approx(<expected>, abs=0.01)
```

**Data size tests** (2-3 tests -- varied and longer sequences):

```python
def test_single_price_point(self, mock_stock_data):
    """Verify <indicator> with only one data point.  SMA/EMA
    produce the value itself; RSI raises IndexError."""
    mock_stock_data([42])
    result = calculate_<indicator>("TEST", 1)
    assert result.iloc[-1] == 42.0

def test_twenty_data_points(self, mock_stock_data):
    """Verify <indicator> works on a 20-point sequence."""
    mock_stock_data(list(range(20)))
    result = calculate_<indicator>("TEST", 5)
    assert len(result) == 1
    assert result.iloc[-1] > 0.0

def test_large_window(self, mock_stock_data):
    """Verify <indicator> with a window close to data length."""
    mock_stock_data(list(range(10)))
    result = calculate_<indicator>("TEST", 8)
    assert len(result) == 1
    assert result.iloc[-1] is not None
```

**Count tests** (2 tests -- the count parameter):

```python
def test_count_multiple(self, mock_stock_data):
    """Verify count returns the last N values."""
    mock_stock_data(list(range(9)))
    result = calculate_<indicator>("TEST", 3, count=3)
    assert len(result) == 3
    assert result.iloc[-1] == pytest.approx(<expected>, abs=0.0001)

def test_count_exceeds_data(self, mock_stock_data):
    """Verify IndexError when count exceeds available values."""
    mock_stock_data([10, 11, 12, 13])
    with pytest.raises(IndexError):
        calculate_<indicator>("TEST", 2, count=5)
```

**Indicator-specific boundary tests** (as needed -- adapt these examples
to your indicator's unique edge cases):

```python
def test_all_gains(self, mock_stock_data):
    """Verify <indicator> produces the expected extreme value
    when every price change is positive."""
    mock_stock_data([10, 11, 12, 13, 14])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == 100.0

def test_all_losses(self, mock_stock_data):
    """Verify <indicator> produces the expected extreme value
    when every price change is negative."""
    mock_stock_data([10, 9, 8, 7, 6])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] == 0.0

def test_constant_prices_edge(self, mock_stock_data):
    """Verify <indicator> handles all-identical prices
    (may raise or return a value)."""
    mock_stock_data([50, 50, 50, 50, 50, 50])
    result = calculate_<indicator>("TEST", 3)
    assert result.iloc[-1] is not None
```

**Data size summary**

| Test | Data size | Window | Count |
|------|-----------|--------|-------|
| test_basic | 6 | 3 | 1 |
| test_window_one | 2 | 1 | 1 |
| test_window_exceeds_data | 3 | 10 | 1 |
| test_insufficient_data | 0 | 5 | 1 |
| test_constant_prices | 6 | 2 | 1 |
| test_alternating_pattern | 8 | 3 | 1 |
| test_large_prices | 5 | 2 | 1 |
| test_negative_prices | 7 | 3 | 1 |
| test_spike_pattern | 10 | 3 | 1 |
| test_single_price_point | 1 | 1 | 1 |
| test_twenty_data_points | 20 | 5 | 1 |
| test_large_window | 10 | 8 | 1 |
| test_count_multiple | 9 | 3 | 3 |
| test_count_exceeds_data | 4 | 2 | 5 |

**Total**: at least 14 unique data sizes.

If the indicator needs columns beyond Close (Open, High, Low, Volume),
update the `mock_stock_data` fixture in `conftest.py` to supply those
columns in the returned DataFrame.

### 3b. Add dispatch tests to `mocktests/test_main.py`

Add two new test methods to the existing `TestMain` class.
The import path to patch remains `"main.calculate_<indicator>"` since
`main.py` re-exports all indicator functions for backward compatibility:

```python
def test_valid_<indicator>_dispatch(self):
    """Verify main() calls calculate_<indicator> for an
    <INDICATOR> input."""
    with patch("builtins.input",
               return_value="AAPL <INDICATOR> 20"):
        with patch("main.calculate_<indicator>",
                   return_value=_MOCK_SERIES) as mock_fn:
            main.main()
            mock_fn.assert_called_once_with(
                "AAPL", 20, interval="1d", count=1)

def test_default_window_<indicator>(self):
    """Verify <INDICATOR> defaults to window=<default> when
    not provided."""
    with patch("builtins.input",
               return_value="AAPL <INDICATOR>"):
        with patch("main.calculate_<indicator>",
                   return_value=_MOCK_SERIES) as mock_fn:
            main.main()
            mock_fn.assert_called_once_with(
                "AAPL", <default>, interval="1d", count=1)
```

Use the existing `_MOCK_SERIES = pd.Series([42.0])` defined at the top of
the file. Place the new methods in alphabetical position among the existing
dispatch tests.

## 4. Real Tests

*(Agent: Test Engineer; reasonableness guidance from the Indicator
Specialist.)*

### 4a. Create `realtests/test_calculate_<indicator>.py`

Create a new file following the pattern in the existing real test files.
These tests call the live yfinance API:

```python
# test_calculate_<indicator>.py
# Integration tests for calculate_<indicator>() with real yfinance
# data

import pytest
from indicators import calculate_<indicator>


class TestCalculate<Indicator>:
    """Tests for calculate_<indicator>() with real yfinance calls."""

    def test_<indicator>_window_5(self):
        """Verify <indicator> for AAPL with window=5 returns a
        positive value."""
        result = calculate_<indicator>("AAPL", 5)
        assert result.iloc[-1] > 0.0

    def test_<indicator>_window_14(self):
        """Verify <indicator> for MSFT with window=14 returns a
        positive value."""
        result = calculate_<indicator>("MSFT", 14)
        assert result.iloc[-1] > 0.0

    def test_<indicator>_window_30(self):
        """Verify <indicator> for GOOG with window=30 returns a
        positive value."""
        result = calculate_<indicator>("GOOG", 30)
        assert result.iloc[-1] > 0.0

    def test_<indicator>_with_weekly_interval(self):
        """Verify <indicator> works with a weekly bar interval."""
        result = calculate_<indicator>("AAPL", 10, interval="1wk")
        assert result.iloc[-1] > 0.0

    def test_<indicator>_same_as_last_close(self):
        """Verify <indicator> with window=1 equals the last close
        price, if applicable."""
        result = calculate_<indicator>("AAPL", 1)
        assert result.iloc[-1] > 0.0
```

### 4b. Add real dispatch test to `realtests/test_main.py`

If the indicator has unique dispatch behaviour, add a test method to the
existing `TestMain` class:

```python
def test_<indicator>_dispatch(self):
    """Verify main() dispatches to <INDICATOR> with default
    interval."""
    with patch("builtins.input",
               return_value="AAPL <INDICATOR> 14"):
        main.main()
```

### 4c. Reasonableness checks

Real tests should verify that indicator outputs are consistent with the
raw data they were computed from. The approach depends on the indicator
type:

**Moving-average indicators (SMA, EMA, VWAP, AV, BB middle band):**

The result of a rolling mean is mathematically guaranteed to fall between
the minimum and maximum of the raw input data. Use the `_return_raw=True`
parameter to retrieve both the indicator result and its raw data in a
single API call:

```python
def test_<indicator>_window_5(self):
    """Verify <indicator> for AAPL with window=5 is within the
    range of its raw input data."""
    result, raw = calculate_<indicator>("AAPL", 5,
                                        _return_raw=True)
    assert raw.min() <= result.iloc[-1] <= raw.max()
```

For BB, additionally verify that the standard deviation is positive
for any window > 1 (confirming price variation exists):

```python
assert raw.iloc[-window:].std(ddof=0) > 0
```

**Bounded oscillators (RSI, STOCH, ADX):**

These indicators are confined to a fixed range by definition, so
verify the bounds hold on real data:

- **RSI**: always verify `0.0 <= result.iloc[-1] <= 100.0`
- **STOCH**: verify `0.0 <= %K <= 100.0` and
  `0.0 <= %D <= 100.0` (both lines)
- **ADX**: verify `0.0 <= value <= 100.0` for all three Series
  (+DI, −DI, ADX) and that the DI lines are non-negative

**Stock-agnostic checks (MACD, RVOL):**

These indicators do not produce a result that is bounded by a single
raw-data series or a fixed range, so use stock-agnostic assertions:

- **MACD**: verify `not m.isna()`, `not s.isna()`, `not h.isna()`
  (all values are finite) and histogram has both positive and
  negative values on a diversified ticker like SPY
- **RVOL**: verify `result > 0.0` and window=1 equals exactly `1.0`

**Raw-bounded volatility (ATR):**

ATR is a weighted average of True Range, so it is guaranteed to fall
within the range of its TR series. Retrieve the raw TR in a single
API call via the `_return_raw=True` parameter:

```python
result, tr = calculate_atr("AAPL", _return_raw=True)
assert tr.min() <= result.iloc[-1] <= tr.max()
```

With `window=1`, ATR equals the latest TR exactly.

**Unbounded momentum and cumulative indicators (CCI, OBV, ROC):**

These have no mathematical upper or lower bound, so verify that the
returned value is present and finite:

- **CCI**: verify `pd.notna(result.iloc[-1])` and
  `np.isfinite(result.iloc[-1])`
- **OBV**: verify `pd.notna(result.iloc[-1])` (cumulative total,
  unbounded)
- **ROC**: verify `pd.notna(result.iloc[-1])`. Optionally bound the
  magnitude on a diversified ticker (e.g.
  `-100 < result < 100` for daily SPY bars) — note this is a
  heuristic sanity band, not a mathematical guarantee

The raw data returned by `_return_raw=True` differs by indicator:

| Indicator | Raw data returned | Source |
|-----------|-------------------|--------|
| SMA | `close` (Series) | `_fetch_close()` |
| EMA | `close` (Series) | `_fetch_close()` |
| BB | `close` (Series) | `_fetch_close()` |
| ATR | `tr` (True Range Series) | `_fetch_ohlcv()` |
| VWAP | `typical` (Series) where TP = (H+L+C)/3 | `_fetch_ohlcv()` |
| AV | `volume` (Series) from OHLCV | `_fetch_ohlcv()` |

## 5. Verification

*(Agent: Test Engineer — quality gate #1 confirmed here.)*

Run the full test suite to check for regressions, then run the new tests
in isolation:

```bash
# All mock tests (fast, no network)
python3 run_mock_tests.py

# New mock test file
pytest mocktests/test_calculate_<indicator>.py -v

# New dispatch tests
pytest mocktests/test_main.py -v -k <indicator>

# All real tests with 1-second spacing between each to avoid yfinance
# rate limits
python3 run_real_tests.py

# A single real test
pytest realtests/test_calculate_<indicator>.py::TestCalculate<Indicator>::test_<indicator>_window_5 -v
```

When running real tests directly with `pytest realtests/` (not through
`run_real_tests.py`), a conftest hook automatically inserts 1 second of
spacing between tests. To disable this (e.g. for parallel execution), set
`REALTEST_NO_SLEEP=1`. Use `python3 run_real_tests.py` to also run with
1-second spacing but with per-test section headers and an overall summary.

## 6. Update README

*(Agent: Documentation Expert; the `6c. Update formulas.md` content
comes from the Indicator Specialist.)*

Update `README.md` to list the new indicator in the Syntax table,
in alphabetical position:

| Token | Meaning | Allowed Values | Default |
|-------|---------|----------------|---------|
| `indicator` | Indicator to compute | `ADX`, `ATR`, `AV`, `BB`, `CCI`, `EMA`, `MACD`, `OBV`, `ROC`, `RSI`, `RVOL`, `SMA`, `STOCH`, `VWAP`, `<INDICATOR>` | Required |

Add a new example command to the Examples section:

```bash
# <full name>
echo "AAPL <INDICATOR> <default_window> C5" | python3 main.py
```

If the default window differs from the existing indicators' norms, add a
row to the default-windows description in the How It Works or Usage
section.

### 6c. Update formulas.md

Add a new section to `docs/formulas.md` for the new indicator, placed
in alphabetical order among the existing sections.  Include:

- The mathematical formula using LaTeX notation (`$$...$$`).
- A table of variables and their meanings.
- Any relevant edge-case notes (division by zero, NaN handling, etc).

The section should follow the same structure as the existing
indicators (e.g. start with a short description, then the formula,
then the variable table, then notes).

## 7. Versioning & Changelog

*(Agent: Release Manager.)*

After completing the implementation, tests, and documentation, follow the
[changelog update process](update_changelog.md) to bump the version and
record the changes.

Adding a new indicator is a **minor** version bump (X.Y+1.0).

After the release is recorded in `CHANGELOG.md`, move the indicator's TODO
entry from **In Progress** to **Done** and check the box (`[x]`).
