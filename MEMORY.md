# Project Memory

Persistent decision and learning log for QuantLab's agent system.
Agents read this at session start and append at session end.

## Decisions Log

<!-- Append decisions with dates. Never rewrite existing entries. -->

- **2026-08-29**: v1.8.0 — agent-based development workflow released.
  11 agents in `agents/`, registered in `.opencode/opencode.json`.
  Gate sequence: test → review → security → consistency → release.
- **2026-08-29**: v1.8.1 — agent system improvements: extracted shared
  conventions to `docs/conventions_reference.md`, created MEMORY.md for
  persistent context, added SKILL.md patterns for complex workflows,
  created `scripts/verify.sh` for automated pre-handoff checks.
- **2026-08-30**: v2.0.0 — backtester added. Entry/exit logic is
  all-conditions-must-match AND fixed hold period. Data cache is
  parquet files (one per ticker per interval). Ticker scope is
  multi-ticker scan using `yf.download()` batching. Condition syntax
  is `INDICATOR [params] [component] OP VALUE INTERVAL`. Known
  limitations: survivorship bias, no transaction costs, no short
  selling, intraday data limits (7/60 day max for minute/hour data).
- **2026-08-30**: v2.0.1 — bug fixes: KeyError 'Close' from
  MultiIndex columns, shell operator aliases (below/above/etc.),
  Sharpe/Sortino NaN std, parameter validation for single-default
  indicators, pyarrow warning suppression, float param crash,
  equity curve inflation fix.
- **2026-08-31**: v2.1.0 — universe/scanner feature. `--universe
  sp500` or `--universe path/to.csv` runs a strategy across all
  S&P 500 stocks or a custom list. `--max-tickers N` limits scope.
  Chunked download (CHUNK_SIZE=50) for large universes. Summary
  reporting mode for 20+ tickers. Wikipedia cache with 24h TTL.

## Corrections & Lessons Learned

<!-- Record mistakes and what was learned from them. -->

- **File naming**: `documentation-expect.md` was a typo for
  `documentation-expert.md`. Always verify agent filenames before
  committing.
- **JSON permissions**: opencode.json agent permission objects must use
  the last-match-wins pattern (`"*": "ask"` first, specific allows
  last) to avoid global allow overriding specific deny.

## Last Session State

<!-- Brief snapshot of where work left off. Updated at end of session. -->

- Current version: 2.0.1
- All 609 mock tests passing (422 existing + 187 backtester tests).
- Operator aliases: `below`/`above`/`at_or_below`/`at_or_above`/`equals`
  avoid shell redirection issues with `<`/`>` characters.
- `yf.download()` returns MultiIndex columns even for single ticker —
  `_download_batch` now flattens the ticker level.
- Ticker validation: 1-10 alphanumeric chars, must contain letter.
- yfinance logger suppressed (set to ERROR during download).
- Failed tickers tracked separately, error messages list specific tickers.
- Equity curve includes daily business-day values (forward-filled from
  trade exits) — Sharpe/Sortino now use actual daily returns.
- Parquet caching silently skips when pyarrow is not installed.
- Sharpe/Sortino use tolerance (std < 1e-12) not exact == 0 for float.
- **CLI params are stored as float, converted to int in both
  `_parse_indicator_args` and `compute_indicator`** — prevents
  "window must be an integer" errors from pandas rolling().
- Bug Fix Protocol added to conventions_reference.md §17: every bug
  fix must add tests, update agent constraints, and log lessons.
- Bugs fixed: _smallest_interval order, reporting Sharpe sign,
  _check_condition unknown ops, NaN entry price guard, hold boundary
  guard, Sharpe/Sortino NaN std, param validation for single-default
  indicators, return_pct decimal vs percentage, float param conversion.
- All agent files have Session Instructions (MEMORY.md + verify.sh)
  and Quick Reference sections.
- Shared conventions live in `docs/conventions_reference.md`.
- Skill files created: `skills/add-indicator/`, `skills/release-cut/`,
  `skills/security-audit/`, `skills/backtester/`.
- Backtester agent added: `agents/backtest-engineer.md`.
- Backtester package created: `backtester/` (cli, data_pipeline,
  batch_indicators, engine, metrics, reporting).
- BACKTEST command integrated into `main.py` dispatch.
- 12 agents total (11 original + backtest-engineer).
- v2.0.0 released and pushed to GitHub.
- v2.1.0 — universe/scanner feature added:
  - `backtester/universe.py` handles S&P 500 Wikipedia scraping,
    CSV loading, and ticker validation.
  - `--universe sp500` or `--universe path/to.csv` with `--max-tickers N`.
  - Chunked download (CHUNK_SIZE=50) prevents rate-limiting.
  - Summary reporting mode for 20+ tickers (top/bottom 5, median, mean).
  - Wikipedia cache TTL is 24 hours.
  - CSV auto-detects ticker column by name patterns.
  - 647 total mock tests (197 backtester + 25 universe + 12 integration).
  - **403 fix**: Wikipedia scraping uses browser-like User-Agent
    header to avoid 403 Forbidden. Falls back to hardcoded S&P 500
    snapshot (~503 tickers) if scraping fails for any reason.
  - **Total return overflow fix**: `compute_total_return` now uses
    equal-weight model (`avg_return * n_trades`) instead of sequential
    compounding. Prevents astronomical values with many trades.
  - **Cooldown**: after a trade exits, the same ticker must wait
    `hold` bars before re-entry (prevents rapid re-trading).
- All agent files updated with universe/scanner constraints.
- conventions_reference.md §18 added for universe conventions.
