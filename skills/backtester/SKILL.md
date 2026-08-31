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
- [ ] Verify CLI parsing works for all example inputs
- [ ] Verify error messages are clear and helpful
- [ ] Verify batch indicators match single-ticker results
- [ ] Verify metrics match expected financial formulas
- [ ] Verify parquet caching works (read/write cycle)
- [ ] Test invalid tickers (misspelled, delisted, special chars) → clean error
- [ ] Test partial download failures (some tickers succeed, some fail)
- [ ] Test complete download failure (all tickers fail, network error)
- [ ] Test empty trades (no signals found) → metrics section handles gracefully
- [ ] Test edge cases: single return, zero std, NaN values in metrics

### Handoff
- [ ] Report to Test Engineer for independent verification
- [ ] If user-facing changes: notify Documentation Expert
- [ ] Append decisions to MEMORY.md at session end

## Key Files

| File | Purpose |
|------|---------|
| `backtester/cli.py` | BACKTEST command parser |
| `backtester/data_pipeline.py` | Batch download + parquet cache |
| `backtester/batch_indicators.py` | Vectorized indicator computation |
| `backtester/engine.py` | Core simulation loop |
| `backtester/metrics.py` | Financial metrics |
| `backtester/reporting.py` | Console output formatting |
| `backtester/cache/` | Parquet cache directory |
| `mocktests/test_backtester.py` | Mock test suite |

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

1. **CLI layer** (`cli.py`): validates ticker format (1-10 alphanumeric
   chars, must contain at least one letter) before sending to engine.
2. **Data pipeline** (`data_pipeline.py`): suppresses yfinance logging,
   tracks failed tickers, prints which tickers failed and why.
3. **Engine** (`engine.py`): when all tickers fail, prints specific
   error with the failed ticker names and possible causes, returns
   empty BacktestResult without crashing.
4. **Metrics** (`metrics.py`): handles edge cases — empty trades list
   (returns all-zero metrics), single return (Sharpe returns 0.0),
   NaN std (returns 0.0 instead of NaN).

Common user errors to handle gracefully:
- Typo in ticker symbol (e.g. APPL instead of AAPL)
- Delisted ticker
- Intraday data beyond yfinance limits
- No entry signals found (strategy too restrictive)
- Zero trades (market conditions didn't match strategy)
