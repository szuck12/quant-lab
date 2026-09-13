# Backtester Skill

Step-by-step workflow for adding, modifying, or debugging the
backtesting engine.

## Trigger

When the Task Orchestrator receives a request involving backtesting,
strategy simulation, or the `BACKTEST` command.

## Agent

Primary: **Backtest Engineer** (`agents/backtest-engineer.md`).

## Checklist

### Understanding the Request
- [ ] Clarify the user's goal (new feature, bug fix, performance, etc.)
- [ ] Identify which `backtester/` modules are affected
- [ ] Check `MEMORY.md` for relevant past decisions

### Implementation
- [ ] Read the affected `backtester/` modules
- [ ] Implement changes following existing patterns
- [ ] Run `ruff check backtester/` — must pass
- [ ] Update or add mock tests in `mocktests/test_backtester.py`
- [ ] Run `python3 run_mock_tests.py` — full suite must pass (521+)

### Verification
- [ ] Verify error messages are clear and helpful
- [ ] Verify batch indicators match single-ticker results
- [ ] Verify metrics match expected financial formulas
- [ ] Verify parquet caching works (read/write cycle)
- [ ] Test invalid tickers (misspelled, delisted, special chars) → clean error
- [ ] Test partial download failures (some tickers succeed, some fail)
- [ ] Test complete download failure (all tickers fail, network error)
- [ ] Test empty trades (no signals found) → metrics section handles gracefully
- [ ] Test edge cases: single return, zero std, NaN values in metrics
- [ ] Verify mark-to-market equity curve updates daily (not just at exits)
- [ ] Verify tickers are simulated on one shared timeline (no per-ticker time reuse)
- [ ] Verify benchmark (SPY) aligns to capital on the strategy's first date
- [ ] Verify pyarrow warning is suppressed when engine is missing

### Handoff
- [ ] Report to Test Engineer for independent verification
- [ ] If user-facing changes: notify Documentation Expert
- [ ] Append decisions to MEMORY.md at session end

## Key Files

| File | Purpose |
|------|---------|
| `backtester/data_pipeline.py` | Batch download + parquet cache |
| `backtester/batch_indicators.py` | Vectorized indicator computation |
| `backtester/engine.py` | Chronological portfolio simulation (day-by-day) |
| `backtester/metrics.py` | Financial metrics |
| `backtester/universe.py` | Universe resolution (S&P 500, CSV) |
| `backtester/cache/` | Parquet cache directory |
| `mocktests/test_backtester.py` | Mock test suite |
| `mocktests/test_universe.py` | Universe module tests (20 tests) |

## Condition Syntax

```
INDICATOR [params] [component] OP VALUE INTERVAL
```

Examples:
- `RSI < 30 1d` — RSI below 30 on daily bars
- `SMA 50 > 200 1d` — 50-day SMA above 200-day SMA
- `STOCH 14,5,5 k > 80 1d` — Stochastic %K above 80
- `BB 20,2 upper > 150 1d` — Bollinger upper band above 150
- `MACD 12,26,9 signal > 0 1d` — MACD signal above 0

## Metrics

| Metric | Formula |
|--------|---------|
| Total Return | Sum of all trade returns |
| Annualized Return | Total return annualized over the test period |
| Sharpe Ratio | Mean daily return / std dev of daily returns |
| Sortino Ratio | Mean daily return / downside deviation |
| Max Drawdown | Largest peak-to-trough decline in equity curve |
| Win Rate | Percentage of winning trades |
| Profit Factor | Gross profit / gross loss |

## Error Handling

When working on the backtester, always ensure:

1. **API validation layer**: validates ticker format (1-10 alphanumeric
   chars, must contain at least one letter) before sending to engine.
2. **Data pipeline** (`data_pipeline.py`): suppresses yfinance logging,
   tracks failed tickers, prints which tickers failed and why. Parquet
   caching silently skips if pyarrow/fastparquet is not installed.
   Large ticker lists are downloaded in chunks of ≤50 to avoid
   rate-limiting.
3. **Engine** (`engine.py`): simulates all tickers on one shared
   chronological timeline (`_simulate_portfolio`) — on each day it
   processes exits, then entries in alphabetical ticker order, stopping
   once cash is exhausted, then marks equity to market. One open
   position per ticker; cooldown of `hold` bars after each exit; open
   positions left open at the end. Universe resolution happens before
   download — `--universe sp500` resolves via Wikipedia with a 24h
   cache and browser-like User-Agent header; falls back to a hardcoded
   S&P 500 snapshot (~503 tickers) if scraping fails.
   `--universe path/to.csv` loads tickers from CSV.
4. **Metrics** (`metrics.py`): consumes the mark-to-market equity curve
   so Sharpe/Sortino use genuine daily returns and drawdown includes
   unrealized P&L. Handles edge cases — empty trades list (returns
   all-zero metrics), zero variance (Sharpe/Sortino return 0.0, using
   tolerance `std < 1e-12`). Profit factor uses dollar P&L; annualized
   return is floored at one month to avoid explosive short-run CAGR.
5. **API/chart** (`api/routes.py`, `EquityChart.tsx`): strategy and
   benchmark curves are aligned to capital on the strategy's first date
   and downsampled to ≤100 points. The chart legend reads
   "Benchmark (SPY)".

Common user errors to handle gracefully:
- Typo in ticker symbol (e.g. APPL instead of AAPL)
- Delisted ticker
- Intraday data beyond yfinance limits
- No entry signals found (strategy too restrictive)
- Zero trades (market conditions didn't match strategy)
- Missing pyarrow (caching silently skipped)
- Invalid CSV file (no ticker column found)
- Empty CSV file
