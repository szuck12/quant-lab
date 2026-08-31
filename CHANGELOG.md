# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-08-31

### Added
- **Web application** — FastAPI backend + React/Vite/TypeScript
  frontend with Recharts charts and Tailwind CSS styling.
- **`GET /api/indicators`** — returns available indicators with
  parameter schemas for dynamic form rendering.
- **`GET /api/periods`** — returns analysis period options
  (1mo through 20yr).
- **`POST /api/backtest`** — runs backtest and returns trades,
  metrics, equity curve, and benchmark comparison.
- **Equity curve chart** — Recharts LineChart showing strategy
  vs benchmark performance over time.
- **Metrics table** — side-by-side comparison of strategy and
  benchmark metrics (return, Sharpe, max drawdown, etc.).
- **Trades table** — scrollable, color-coded P&L with
  multi-ticker support.
- **Period selector** — 10 period options from 1 month to 20 years.
- **Dynamic indicator params** — form renders inputs based on
  indicator schema from the API.
- **CORS support** — backend allows Vite dev server on port 5173.
- **Vite proxy** — `/api` and `/health` requests proxied to
  FastAPI backend on port 8000.
- **Web-developer agent** — new agent in `agents/` and
  `.opencode/opencode.json` for web app development.
- **Webapp skill** — `skills/webapp/SKILL.md` workflow for
  web app features.
- **API tests** — 17 tests in `mocktests/test_api.py` covering
  indicators endpoint, periods endpoint, backtest endpoint,
  validation, and error handling.
- **Web conventions** — §19 added to `docs/conventions_reference.md`.
- **Legacy CLI mode** — `python main.py backtest <args>` still
  works alongside the web server.

### Changed
- **`main.py` simplified** — primary entry is now `python main.py`
  which starts uvicorn. CLI dispatch moved to legacy mode.
- **`requirements.txt`** — added `fastapi`, `uvicorn[standard]`,
  `pydantic`.
- **`.gitignore`** — added `web/node_modules/` and `web/dist/`.
- **`AGENTS.md`** — added Web Developer to roster, routing,
  file ownership, and skills index.
- **`MEMORY.md`** — v3.0.0 web application decisions logged.

### Preserved
- **`indicators/` package** — kept for internal use by backtester
  and web API. Not deleted.
- **Backtester engine** — `backtester/` package unchanged. All
  existing features work via the API.

## [2.1.0] - 2026-08-31

### Added
- **Universe / Scanner** — run a strategy across all S&P 500 stocks
  or a custom CSV ticker list: `--universe sp500` or
  `--universe path/to.csv`.
- **`--max-tickers N`** — limit the universe to N tickers for quick
  testing.
- **S&P 500 cache** — Wikipedia ticker list cached 24 hours
  (`backtester/universe.py`).
- **CSV ticker loader** — auto-detects ticker column by name
  (`Ticker`, `Symbol`, `Stock`, `Code`), falls back to first column.
- **Chunked download** — large ticker lists split into chunks of 50
  to avoid yfinance rate-limiting.
- **Summary reporting** — compact output (top/bottom 5, median, mean)
  when ≥20 tickers have trades.
- **Ticker validation** — rejects invalid tickers (1–10 chars, must
  contain a letter) before calling yfinance.
- **Wikipedia scraping fallback** — browser-like User-Agent header
  to avoid 403 errors; falls back to hardcoded S&P 500 snapshot
  (~503 tickers) if scraping fails.
- **Universe tests** — 25 tests in `mocktests/test_universe.py`,
  12 integration tests in `mocktests/test_backtester.py` §20.

### Changed
- `backtester/data_pipeline.py` — `_download_batch` now splits into
  `CHUNK_SIZE=50` chunks; extracts `_download_chunk` helper.
- `backtester/reporting.py` — `format_results` dispatches to
  `_format_summary` when ≥20 tickers have trades.
- `backtester/engine.py` — `run()` calls `resolve_universe()` before
  download; supports `universe` and `max_tickers` config keys.

### Fixed
- **Total return overflow** — `compute_total_return` used sequential
  compounding which produced astronomical values (9.9e15%) with
  many trades. Now uses equal-weight model (`avg_return * n_trades`).
- **Rapid re-trading** — after a trade exits, the same ticker can
  now re-enter immediately. Added cooldown of `hold` bars between
  trades on the same ticker.

## [2.0.1] - 2026-08-30

### Fixed
- **KeyError: 'Close'** — `yf.download()` returns MultiIndex columns even
  for a single ticker; `_download_batch` now flattens the ticker level.
- **Shell operator aliases** — `below`, `above`, `at_or_below`, etc.
  added so BACKTEST commands work without shell quoting.
- **Sharpe/Sortino NaN std** — single-return edge case now returns 0.0
  instead of NaN.
- **Parameter validation** — single-default indicators (RSI, SMA, etc.)
  now reject >1 params instead of crashing at compute time.

### Changed
- README backtester documentation expanded with operator alias table,
  indicator reference, interval list, how-it-works section, and
  known limitations.
- Test suite expanded to 161 backtester tests (from 99).

## [2.0.0] - 2026-08-30

### Added
- `backtester/` package: complete backtesting engine with CLI parser,
  batch data pipeline, vectorized indicator computation, strategy
  simulation, and financial metrics.
- `backtester/cli.py`: BACKTEST command parser with condition syntax,
  multi-ticker support, and CLI options (hold, capital, benchmark,
  years, stop-loss).
- `backtester/data_pipeline.py`: batch data download via `yf.download()`
  with parquet caching.
- `backtester/batch_indicators.py`: vectorized indicator computation
  on DataFrames for all 14 indicators.
- `backtester/engine.py`: core simulation loop with AND-logic condition
  evaluation, fixed hold period, and stop-loss handling.
- `backtester/metrics.py`: financial metrics (total return, annualized
  return, Sharpe ratio, Sortino ratio, max drawdown, win rate,
  profit factor).
- `backtester/reporting.py`: console output formatting with per-ticker
  breakdown and portfolio summary.
- `agents/backtest-engineer.md`: new agent persona for backtester work.
- `skills/backtester/SKILL.md`: backtester workflow checklist.
- `mocktests/test_backtester.py`: 99 comprehensive mock tests covering
  CLI parsing, batch indicators, data pipeline, engine simulation,
  metrics, and reporting.

### Changed
- `main.py`: integrated BACKTEST command into the match/case dispatch.
- `AGENTS.md`: added backtest-engineer to roster, routing, file
  ownership, and skills index.
- `.opencode/opencode.json`: registered backtest-engineer agent.
- `docs/conventions_reference.md`: added §16 (backtester conventions).
- 8 existing agent files: added backtester responsibilities.
- Version bump from 1.8.1 to 2.0.0.

### Known Limitations
- Survivorship bias: only currently listed tickers are tested.
- No transaction costs or slippage modeled.
- No short selling support.
- Intraday data limited to 7 days (minute) / 60 days (hour) by
  yfinance.
- Condition syntax requires operator and value as separate tokens.

## [1.8.1] - 2026-08-29

### Added
- `MEMORY.md`: persistent decision and learning log for agent sessions.
- `docs/conventions_reference.md`: single source of truth for all shared
  conventions (code style, alphabetical ordering, indicator patterns,
  TODO/CHANGELOG formatting, gate sequence, semver rules).
- `skills/` directory with SKILL.md playbooks for complex workflows:
  `add-indicator` (orchestrator checklist + implementer/tester templates),
  `release-cut` (gate sequence + checklist), `security-audit` (scan
  commands + severity scale).
- `scripts/verify.sh`: pre-handoff verification script (lint, smoke test,
  full mock suite).

### Changed
- All 11 agent files: added Session Instructions (MEMORY.md + verify.sh)
  and Quick Reference sections; conventions extracted to shared reference.
- `AGENTS.md`: trimmed from 187 to 121 lines, added Skills Index and
  MEMORY.md ownership, per-agent usage moved to agent Quick References.
- `.opencode/opencode.json`: all agent prompts updated with MEMORY.md,
  verify.sh, and skill references.

## [1.8.0] - 2026-08-29

### Added
- Agent-based development workflow: eleven specialized agent personas in
  `agents/` (Task Orchestrator, Idea Generator, Feature Implementer,
  Indicator Specialist, Data Engineer, Test Engineer, Code Reviewer,
  Consistency Guardian, Documentation Expert, Security Auditor, Release
  Manager), each with role, scope, operating instructions,
  interactions, and a handoff checklist.
- `AGENTS.md` usage guide: roster, routing table, file ownership,
  invocation, handoff and gate rules, and per-agent usage.
- `docs/agents_overview.md` and `docs/agent_workflows.md`: the agent
  interaction model and step-by-step workflows naming the responsible
  agent for each step.
- opencode registration (`.opencode/opencode.json`) binding each agent
  persona to its file so the agents are directly invocable.
- Existing process documentation (`adding_indicator.md`,
  `maintain_todo.md`, `update_changelog.md`, `code_review_guide.md`,
  `commenting_guidelines.md`, `formulas.md`, `SECURITY.md`) now names
  the agents responsible for each step and surface.
- `TODO.md` entries now carry `@agent` owner tags
  (e.g. `@security-auditor @test-engineer`).

### Added
- Security policy (SECURITY.md) describing private vulnerability
  reporting and disclosure style.
- Automated weekly dependency-update checks.

### Changed
- Project documentation now states that security topics are
  discussed only in general terms across all committed artifacts.

### Security
- Fixed 1 known security vulnerability in pinned dependencies.

## [1.7.2] - 2026-08-22

### Added
- Section 9 (Security Vulnerability Review) in the code review
  guide: threat model, four-level severity scale with reporting
  protocol, and seven vulnerability-class checklists with
  verification commands.

### Changed
- Ticker symbols are sanitised before being echoed to output
  (escape sequences and control characters stripped).
- requirements.txt now pins exact versions of yfinance, pandas,
  and pytest instead of open lower bounds.
- .gitignore covers local tool caches (.mypy_cache/, .ruff_cache/).
- Dependabot alerts enabled for the repository.

## [1.7.1] - 2026-08-22

### Changed
- Documentation sync with the fourteen-indicator codebase: the code
  review guide's reasonableness-check table (section 4b) now covers
  ADX, ATR, CCI, OBV, ROC, and STOCH; stale indicator counts,
  fetcher/raw-data tables, `_return_raw` list, main.py size notes,
  and example indicator lists updated across docs.
- README error-message table now lists all four ADX parameter-error
  paths.

## [1.7.0] - 2026-08-15

### Added
- Commodity Channel Index (CCI) — new unbounded oscillator
  comparing the Typical Price (H + L + C) / 3 to its SMA and
  normalising by 0.015 times the Mean Deviation (average
  absolute distance from the window's SMA, not a standard
  deviation).  Default window 20, matching TradingView's
  ta.cci().
- 18 mock tests and 5 real tests for CCI.
- CCI dispatch tests in both test suites.
- 422 mock tests, 87 real tests (was 402 mock, 81 real).

## [1.6.0] - 2026-07-05

### Added
- Average Directional Index (ADX) — new trend-strength indicator
  implementing Wilder's Directional Movement system: +DI and −DI
  (directional movement smoothed with Wilder RMA and normalised
  by True Range) plus ADX, the RMA of DX.  Defaults (14, 14) via
  comma-separated syntax (e.g. "14,14"), matching TradingView's
  ta.dmi().
- 19 mock tests and 5 real tests for ADX.
- ADX dispatch tests in both test suites.
- 402 mock tests, 81 real tests (was 381 mock, 75 real).

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

