---
name: add-indicator-test-mock
description: Mock test template for a new indicator. Loaded by the Test Engineer during the add-indicator workflow.
---

# Mock Test Template — New Indicator

## Overview

This file contains the mock test template for new indicators.
Referenced by `skills/add-indicator/SKILL.md` Step 5.

## File Location

`mocktests/test_calculate_<indicator>.py`

## Required Test Categories (14+)

Every mock test file must cover these categories with at least the
minimum data sizes shown:

| Category | Data Sizes | What to Assert |
|----------|-----------|----------------|
| Reference test | 6 | `pytest.approx` with specialist values |
| Window = 1 | 2 | Result equals last data value |
| Window > data | 3 | `IndexError` or valid fallback |
| Insufficient data | 0 | `pytest.raises(IndexError)` |
| Constant prices | 6 | Result equals the constant |
| Alternating | 8 | Matches expected rolling value |
| Large prices (~1e9) | 5 | No overflow |
| Negative prices | 7 | Handled without error |
| Spike | 10 | One outlier in flat series |
| Single price point | 1 | Works or raises correctly |
| 20 data points | 20 | Large sequence |
| Window near length | 10 | Edge of available data |
| Count = 3 | 3 | Multiple values returned |
| Count > available | 2 | `IndexError` |

## Dispatch Test

Add to `mocktests/test_main.py`:

```python
def test_valid_<indicator>_dispatch(self):
    """Verify main() calls calculate_<indicator>."""
    with patch("builtins.input",
               return_value="AAPL <INDICATOR> 20"):
        with patch("main.calculate_<indicator>",
                   return_value=_MOCK_SERIES) as mock_fn:
            main.main()
            mock_fn.assert_called_once_with(
                "AAPL", 20, interval="1d", count=1)
```

## Reasonableness Checks

Use the correct assertion per indicator class (see
`docs/conventions_reference.md` §9):

| Class | Assertion |
|-------|-----------|
| Moving-average | `min <= result <= max` on raw data |
| Bounded oscillator | `0 <= result <= 100` |
| Stock-agnostic | Finite values, no NaN |
| Raw-bounded volatility | `min(TR) <= result <= max(TR)` |
| Unbounded momentum | `pd.notna()` and `np.isfinite()` |

## Verification

```bash
python3 run_mock_tests.py
```

Full suite must be green. Never run a single file for gating.
