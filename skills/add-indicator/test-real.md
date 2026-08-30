---
name: add-indicator-test-real
description: Real test template for a new indicator. Loaded by the Test Engineer during the add-indicator workflow.
---

# Real Test Template — New Indicator

## Overview

This file contains the real test template for new indicators.
Referenced by `skills/add-indicator/SKILL.md` Step 6.

## File Location

`realtests/test_calculate_<indicator>.py`

## Required Coverage

Every real test file must include:

- **3+ tickers**: AAPL, MSFT, GOOG (or similar liquid tickers).
- **3+ window sizes**: small (e.g. 5), medium (e.g. 20), large
  (e.g. 50).
- **Weekly interval variant**: test with `interval="1wk"`.
- **Window=1 variant**: where meaningful (result equals last value).
- **Dispatch test**: in `realtests/test_main.py`.

## Assertion Pattern

```python
def test_<indicator>_basic(self):
    """Verify <indicator> produces valid output for AAPL."""
    result = calculate_<indicator>("AAPL", window=20)
    assert len(result) > 0
    assert pd.notna(result).all()
    # Reasonableness check per indicator class:
    assert result.min() >= 0  # e.g. for bounded oscillator
```

## Dispatch Test (Real)

Add to `realtests/test_main.py`:

```python
def test_valid_<indicator>_dispatch(self):
    """Verify main() handles <INDICATOR> input."""
    with patch("builtins.input",
               return_value="AAPL <INDICATOR> 20"):
        result = main.main()
        assert result is not None
```

## Rate Limiting

Real tests hit yfinance. Respect 1s spacing (configured in
`conftest.py`). Use `REALTEST_NO_SLEEP=1` only for parallel execution.

## Verification

```bash
python3 run_real_tests.py
```

Requires network. Skip if offline; report as blocked.
