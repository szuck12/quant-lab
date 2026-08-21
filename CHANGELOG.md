# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-06-19

### Added
- On-Balance Volume (OBV) — new cumulative momentum indicator that
  adds each bar's volume to a running total on up closes and
  subtracts it on down closes (default window 30; the window sets
  how much history is fetched since OBV accumulates from the
  first bar).
- 17 mock tests and 5 real tests for OBV.
- OBV dispatch tests in both test suites.
- 381 mock tests, 75 real tests (was 362 mock, 69 real).

## [1.4.0] - 2026-06-16

### Added
- Rate of Change (ROC) — new momentum indicator measuring the
  percentage change in close price over a configurable window
  (default 9, matching TradingView).
- 17 mock tests and 5 real tests for ROC.
- ROC dispatch tests in both test suites.
- 362 mock tests, 69 real tests (was 343 mock, 63 real).

## [1.3.0] - 2026-05-27

### Added
- Average True Range (ATR) — new indicator measuring market volatility
  using Wilder-smoothed True Range over a configurable window (default 14).
- Stochastic Oscillator (STOCH) — new indicator comparing close to the
  high-low range, with SMA-smoothed %K and %D lines (default 14,3,3).
- Alphabetised all indicator references across README, docs, and code
  (ATR, AV, BB, EMA, MACD, RSI, RVOL, SMA, STOCH, VWAP).
- 15 mock tests and 5 real tests for ATR.
- 14 mock tests and 5 real tests for STOCH.
- ATR and STOCH dispatch tests in both test suites.
- 343 mock tests, 63 real tests (was 327 mock, 58 real).

## [1.2.3] - 2026-05-25

### Added
- `sys.argv` support: arguments can now be passed directly on the
  command line (`python3 main.py AAPL SMA 50`) without requiring stdin.

### Changed
- Extracted indicator calculation logic from `main.py` into a dedicated
  `indicators/` subpackage (one file per indicator) for improved
  testability, merge hygiene, and onboarding.

## [1.2.2] - 2026-05-25

### Added
- Formulas documentation — `docs/formulas.md` with mathematical
  formulas and explanations for all eight indicators (SMA, EMA, RSI,
  MACD, BB, VWAP, AV, RVOL).  README and contributing docs updated
  to reference it.
- Default window parameters for `calculate_sma(50)`, `calculate_ema(20)`,
  and `calculate_rsi(14)` function signatures, matching `_DEFAULT_WINDOWS`.

### Fixed
- MACD real tests: replaced market-condition-dependent `m > 0` assertions
  with stock-agnostic `notna()` checks.
- yfinance error handling: `_fetch_ohlcv` now catches network/ticker
  exceptions and returns an empty DataFrame instead of crashing.
- Multi-ticker failure isolation: a calculation failure for one ticker
  no longer aborts remaining tickers in the same input (wrapped dispatch
  in per-ticker try/except).

## [1.2.1] - 2026-05-22

### Added
- Reasonableness checks for SMA, EMA, VWAP, AV, and BB real tests —
  each result is verified to fall within the min-max range of its raw
  input data, catching data source and calculation errors.  Increased
  specificity of indicator testing (25 assertions added across 5 files).
  No extra API calls required.

## [1.2.0] - 2026-05-21

### Added
- Average Volume (AV) indicator — simple rolling mean of Volume
  over a configurable window, matching the SMA pattern applied to
  volume data.  Supports all bar intervals.
- Relative Volume (RVOL) indicator — ratio of current Volume to
  its rolling mean over a configurable window.  Values > 1.0
  indicate above-average volume; < 1.0 below-average.  Default
  window of 10 matches TradingView's standard.
- 16 mock tests and 5 real tests for AV.
- 15 mock tests and 5 real tests for RVOL.
- AV and RVOL dispatch tests in both test suites.

## [1.1.0] - 2026-05-20

### Added
- Bollinger Bands (BB) indicator — upper, middle, and lower bands
  based on SMA and population standard deviation (ddof=0, matching
  TradingView's ta.bb()).  Configurable window and number of
  standard deviations via comma-separated syntax (e.g. "20,2.5").
- Volume Weighted Average Price (VWAP) indicator — rolling sum of
  Typical Price × Volume divided by rolling sum of Volume,
  matching TradingView's ta.vwap().
- 16 mock tests and 6 real tests for BB.
- 15 mock tests and 5 real tests for VWAP.
- BB and VWAP dispatch tests in both test suites.

## [1.0.0] - 2026-05-18

### Added

- CLI entry point with stdin-based argument parsing — ticker, indicator,
  bar interval, window, and C<N> count tokens accepted in any order.
- Four technical indicators:
  - **SMA** — simple rolling mean over a configurable window.
  - **EMA** — exponential moving average (span-based, adjust=False).
  - **RSI** — relative strength index with Wilder smoothing
    (alpha = 1 / window).
  - **MACD** — EMA(fast) − EMA(slow), signal line, and histogram with
    configurable periods.
- 13 bar intervals (1m through 3mo) with a data period mapping system.
- Multi-ticker support via comma-separated symbols.
- C\<N\> count syntax for returning multiple historical values.
- Comprehensive input validation with descriptive error messages.
- Mock test suite (242 tests) with patched yfinance for deterministic
  execution.
- Real integration test suite (30 tests) with live yfinance API.
- Automatic 1-second spacing between real tests when running
  `pytest realtests/` (conftest hook), disabled via `REALTEST_NO_SLEEP=1`.
- Convenience runners — `run_mock_tests.py` and `run_real_tests.py`.
- Documentation: README, adding_indicator guide, commenting_guidelines,
  update_changelog process.
- MIT License.

