# Code Review Guide

Checklist for reviewing changes before committing. Each step is ordered by
increasing time cost — stop early if a blocker is found.

## 1. Smoke Check

- [ ] `python3 run_mock_tests.py` passes (306 tests at baseline).
- [ ] If real tests were modified: `python3 run_real_tests.py` passes.
- [ ] If `main.py` changed: basic CLI smoke test works:
      ```bash
      echo "AAPL SMA 5" | python3 main.py
      ```

## 2. Code Consistency

- [ ] Google-style docstrings on every public function (maintain indentation,
      80-char wrap, `Args:` / `Returns:` / `Raises:`).
- [ ] Type hints on every function signature.
- [ ] No inline comments that restate the obvious (e.g. `# calculate mean`).
- [ ] Two blank lines between top-level definitions (PEP 8).
- [ ] 80-character line limit everywhere.
- [ ] `_fetch_close` is used (not `get_stock_data` — removed in v1.2.0).

## 3. Indicator-Specific Checks

- [ ] New indicator registered in:
  - `_DEFAULT_WINDOWS` dict
  - `main()` input prompt string
  - `main()` validation set
  - `main()` match/case dispatch block
- [ ] Default window matches TradingView (or was explicitly agreed otherwise).
- [ ] Edge cases handled: division by zero, NaN/empty series, window >
      data length, all-constant input, insufficient count.
- [ ] `_data_period(window + count, interval)` — not just `window`.

## 4. Test Coverage (Mock)

- [ ] Reference test with known-answer assertion.
- [ ] Window edge tests: `window=1`, `window > len(data)`, empty data.
- [ ] Data pattern tests: constant, alternating, large (~1e9), negative,
      spike.
- [ ] Data size tests: single point, 20 points, window close to length.
- [ ] Count tests: `count=3`, `count > available`.
- [ ] Indicator-specific boundary tests (e.g. all-gains / all-losses for RSI,
      zero-volume for VWAP).
- [ ] Dispatch tests in `mocktests/test_main.py`: `test_valid_*_dispatch`
      and `test_default_window_*`.

## 5. Test Coverage (Real)

- [ ] At least 3 different tickers with different windows.
- [ ] Weekly interval variant (if applicable).
- [ ] Window=1 variant (if meaningful).
- [ ] Reasonableness check: for moving-average indicators (SMA, EMA,
      VWAP, AV, BB), verify the result is within the min-max range of
      the raw input data using `_return_raw=True`.
- [ ] Added to `realtests/test_main.py` if dispatch behaviour is unique.

## 6. Documentation

- [ ] `README.md` Syntax table updated.
- [ ] `README.md` example command added.
- [ ] `TODO.md` moved from **In Progress** → **Done** with `[x]`.
- [ ] `CHANGELOG.md` updated with version bump (minor for new indicators).

## 7. Commit Hygiene

- [ ] Only intended files staged (`git status` / `git diff --cached`).
- [ ] `git diff --cached` reviewed for accidental debug prints or secrets.
- [ ] Commit message format: `<type>(<scope>): <description>`.
