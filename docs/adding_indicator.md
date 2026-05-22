# Adding a New Indicator

This document describes the process for adding a new technical indicator to
quant_indicators. Follow these steps in order. Each step references the
existing SMA, EMA, RSI, and MACD implementations as templates.

## 0. Create a TODO Entry

Before implementing, add a TODO item to `TODO.md` (see
[docs/maintain_todo.md](maintain_todo.md)).  Determine the priority based on
how important the change is — requested changes are not automatically high
priority.  Use an unchecked box (`[ ]`) and move the item to **In Progress**
once you start implementation.

## 1. Information to Gather

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

## 2. Implementation in `main.py`

### 2a. Add the `calculate_*` function

Add a new function following the same signature pattern as the existing
indicators:

```python
def calculate_<indicator>(ticker: str, window: int,
                          interval: str = "1d",
                          count: int = 1) -> pd.Series:
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

Place the new function below the existing indicators (after `calculate_macd`)
and above `main()`. Separate it from neighbouring functions with two blank
lines (PEP 8).

### 2b. Add a default window to `_DEFAULT_WINDOWS`

Add one entry to the `_DEFAULT_WINDOWS` dictionary:

```python
_DEFAULT_WINDOWS: dict[str, int] = {
    "SMA": 50,
    "EMA": 20,
    "RSI": 14,
    "<INDICATOR>": <default_window>,
}
```

### 2c. Register the indicator in `main()`

Three changes inside `main()`:

1. **Prompt** — add the new indicator name to the list shown to the user
   in the `input()` call:
   ```python
   user_input = input("Enter ticker(s), indicator (SMA/RSI/EMA/<INDICATOR>)"
                      " [bar_size] [window] [C<count>]: ")
   ```

2. **Validation set** — add the uppercased name to the
   `indicator.upper()` check:
   ```python
   indicator = indicator.upper()
   if indicator not in ("SMA", "RSI", "EMA", "<INDICATOR>"):
   ```

3. **Dispatch match/case** — add a new case block inside the
   `match indicator:` block:
   ```python
   case "<INDICATOR>":
       result = calculate_<indicator>(ticker, window,
                                      interval=interval,
                                      count=count)
   ```

### 2d. Follow the commenting guidelines

Follow the [commenting guidelines](commenting_guidelines.md) for docstring
style, type hints, inline comments, and line length.

## 3. Mock Tests

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

Add two new test methods to the existing `TestMain` class:

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
the file. Place the new methods after the existing dispatch tests (after
`test_default_window_rsi`).

## 4. Real Tests

### 4a. Create `realtests/test_calculate_<indicator>.py`

Create a new file following the pattern in the existing real test files.
These tests call the live yfinance API:

```python
# test_calculate_<indicator>.py
# Integration tests for calculate_<indicator>() with real yfinance
# data

import pytest
from main import calculate_<indicator>


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

## 5. Verification

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

Update `README.md` to list the new indicator in the Syntax table:

| Token | Meaning | Allowed Values | Default |
|-------|---------|----------------|---------|
| `indicator` | Indicator to compute | `SMA`, `EMA`, `RSI`, `<INDICATOR>` | Required |

Add a new example command to the Examples section:

```bash
# <full name>
echo "AAPL <INDICATOR> <default_window> C5" | python3 main.py
```

If the default window differs from the existing indicators' norms, add a
row to the default-windows description in the How It Works or Usage
section.

## 7. Versioning & Changelog

After completing the implementation, tests, and documentation, follow the
[changelog update process](update_changelog.md) to bump the version and
record the changes.

Adding a new indicator is a **minor** version bump (X.Y+1.0).

After the release is recorded in `CHANGELOG.md`, move the indicator's TODO
entry from **In Progress** to **Done** and check the box (`[x]`).
