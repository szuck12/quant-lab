# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

