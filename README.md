# QuantLab

Current version: **2.0.0** — [Changelog](CHANGELOG.md)

A command-line tool that fetches stock price data via [yfinance](https://github.com/ranaroussi/yfinance) and computes one of fourteen technical indicators: Average Directional Index (ADX), Average True Range (ATR), Average Volume (AV), Bollinger Bands (BB), Commodity Channel Index (CCI), Exponential Moving Average (EMA), Moving Average Convergence Divergence (MACD), On-Balance Volume (OBV), Rate of Change (ROC), Relative Strength Index (RSI), Relative Volume (RVOL), Simple Moving Average (SMA), Stochastic Oscillator (STOCH), or Volume Weighted Average Price (VWAP). Input is provided through stdin and the result is printed to stdout. The tool is designed for quick terminal lookups — you type a ticker and an indicator, and you get back a number.

As of v2.0.0, QuantLab also includes a **backtester** that runs multi-condition strategies across multiple tickers with batch data download and parquet caching.

yfinance provides access to Yahoo Finance market data. The tool does not require an API key or account.

## Installation

Requires Python 3.12+ (tested on 3.12; may work on 3.x).

```bash
pip install -r requirements.txt
```

`requirements.txt` installs three packages:

| Package | Purpose |
|---------|---------|
| `yfinance` | Fetches stock price history from Yahoo Finance |
| `pandas` | Performs rolling window and exponential moving average calculations |
| `pytest` | Test runner (not required for the CLI, required for running tests) |

## Command-Line Usage

Input is read from stdin. The parser accepts a line of space-separated tokens.

### Syntax

```
ticker(s) indicator [bar_size] [window] [C<count>]
```

| Token | Meaning | Allowed Values | Default |
|-------|---------|----------------|---------|
| `ticker(s)` | Stock symbol(s), comma-separated | Any symbol yfinance recognises (e.g. AAPL, MSFT, GOOG, SPY, BTC-USD, EURUSD=X) | Required |
| `indicator` | Indicator to compute | `ADX`, `ATR`, `AV`, `BB`, `CCI`, `EMA`, `MACD`, `OBV`, `ROC`, `RSI`, `RVOL`, `SMA`, `STOCH`, `VWAP` (case-insensitive) | Required |
| `bar_size` | Width of each price bar | `1m`, `2m`, `5m`, `15m`, `30m`, `90m`, `60m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` | `1d` |
| `window` | Lookback period in bars (for MACD: comma-separated fast,slow,signal, e.g. `12,26,9`; for BB: comma-separated window,num_std, e.g. `20,2.5`; for STOCH: comma-separated window,smooth_k,smooth_d, e.g. `14,3,3`; for ADX: comma-separated window,adx_window, e.g. `14,14`) | Any positive integer, or comma-separated values for MACD/BB/STOCH/ADX | ADX=(14,14), ATR=14, AV=20, BB=(20,2.0), CCI=20, EMA=20, MACD=(12,26,9), OBV=30, ROC=9, RSI=14, RVOL=10, SMA=50, STOCH=(14,3,3), VWAP=20 |
| `C<count>` | Number of recent values to return | `C` followed by any positive integer (e.g. `C1`, `C10`, `C100`) | `1` |

### Backtester Syntax

```
python3 main.py BACKTEST ticker(s) <INDICATOR [params] [component] OP VALUE INTERVAL> [options]
```

**Shell quoting**: The `<` and `>` characters are shell operators. You **must** either quote them or use word-based aliases (see below):

```bash
# These all work:
python3 main.py BACKTEST AAPL RSI below 30 1d        # word-based aliases
python3 main.py BACKTEST AAPL RSI '<' 30 1d           # single quotes
python3 main.py BACKTEST AAPL RSI "<" 30 1d           # double quotes
python3 main.py BACKTEST AAPL RSI \\< 30 1d           # escaped

# This will fail in zsh/bash:
python3 main.py BACKTEST AAPL RSI < 30 1d             # ERROR: shell interprets <
```

#### Operator Aliases

Instead of symbol operators, use these word-based aliases (case-insensitive):

| Symbol | Alias(es) |
|--------|-----------|
| `<` | `below`, `under`, `less_than`, `lt` |
| `>` | `above`, `over`, `greater_than`, `gt` |
| `<=` | `at_or_below`, `at_most`, `lte` |
| `>=` | `at_or_above`, `at_least`, `gte` |
| `=` | `equals`, `equal_to`, `eq` |

#### Token Reference

| Token | Meaning | Example |
|-------|---------|---------|
| `BACKTEST` | Command keyword | `BACKTEST` |
| `ticker(s)` | Stock symbol(s), comma-separated | `AAPL,MSFT` |
| `<INDICATOR ...>` | One or more conditions (each must end with interval) | `RSI below 30 1d` |
| `--hold N` | Hold period in bars (default: 10) | `--hold 5` |
| `--capital N` | Starting capital (default: 10000) | `--capital 50000` |
| `--benchmark TICKER` | Benchmark ticker (default: SPY) | `--benchmark QQQ` |
| `--years N` | Years of history (default: 2) | `--years 3` |
| `--stop-loss N` | Stop-loss percentage (default: disabled) | `--stop-loss 5` |
| `--universe SOURCE` | Run strategy across a ticker universe (`sp500` or CSV path) | `--universe sp500` |
| `--max-tickers N` | Limit universe to N tickers (default: all) | `--max-tickers 50` |

#### Condition Format

```
INDICATOR [params] [component] OP VALUE INTERVAL
```

- **Simple**: `RSI below 30 1d`, `SMA 50 above 200 1d`
- **With params**: `STOCH 14,5,5 k above 80 1d`, `BB 20,2 upper above 150 1d`
- **With component**: `MACD 12,26,9 signal above 0 1d`
- **Multiple conditions (AND logic)**: `RSI below 30 1d SMA 50 above 200 1d`

### Backtester Examples

```bash
# Basic RSI oversold strategy (word-based aliases, no quoting needed)
python3 main.py BACKTEST AAPL RSI below 30 1d

# Multi-condition strategy
python3 main.py BACKTEST AAPL,MSFT RSI below 30 1d SMA 50 above 200 1d

# Custom hold period and capital
python3 main.py BACKTEST AAPL RSI below 30 1d --hold 5 --capital 50000

# With stop-loss
python3 main.py BACKTEST AAPL RSI below 30 1d --stop-loss 5

# Using escaped shell operators
python3 main.py BACKTEST AAPL RSI \< 30 1d

# Bollinger Bands breakout
python3 main.py BACKTEST AAPL BB 20,2 upper above 150 1d

# MACD signal crossover
python3 main.py BACKTEST AAPL MACD 12,26,9 signal above 0 1d

# Stochastic overbought
python3 main.py BACKTEST AAPL STOCH 14,5,5 k above 80 1d

# Universe scan: run RSI oversold strategy across all S&P 500 stocks
python3 main.py BACKTEST --universe sp500 RSI below 30 1d

# Universe with ticker limit
python3 main.py BACKTEST --universe sp500 --max-tickers 50 RSI below 30 1d

# Universe from CSV file
python3 main.py BACKTEST --universe my_tickers.csv RSI below 30 1d

# Weekly timeframe
python3 main.py BACKTEST AAPL RSI below 30 1wk

# 3 years of data, custom benchmark
python3 main.py BACKTEST AAPL,MSFT RSI below 30 1d --years 3 --benchmark QQQ
```

### Supported Indicators

| Indicator | Parameters | Components | Default Window |
|-----------|-----------|------------|----------------|
| ADX | `di_len,adx_len` | — | `14,14` |
| ATR | `window` | — | `14` |
| AV | `window` | — | `20` |
| BB | `window,num_std` | `upper`, `middle`, `lower` | `20,2.0` |
| CCI | `window` | — | `20` |
| EMA | `window` | — | `20` |
| MACD | `fast,slow,signal` | `macd`, `signal`, `hist` | `12,26,9` |
| OBV | `window` | — | `30` |
| ROC | `window` | — | `9` |
| RSI | `window` | — | `14` |
| RVOL | `window` | — | `10` |
| SMA | `window` | — | `50` |
| STOCH | `window,smooth_k,smooth_d` | `k`, `d` | `14,3,3` |
| VWAP | — | — | — |

### Valid Intervals

| Interval | Description |
|----------|-------------|
| `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h` | Intraday |
| `1d` | Daily |
| `1wk` | Weekly |
| `1mo`, `3mo` | Monthly |

**Intraday limits**: 1m data is limited to 7 days, 2m–15m to 60 days, 30m–90m to 60 days.

### How the Backtester Works

1. **Data download**: Uses `yfinance` to batch-download OHLCV data for all tickers and the benchmark. Data is cached as Parquet files (requires `pyarrow` or `fastparquet`).
2. **Indicator computation**: Computes all requested indicators on each ticker's data.
3. **Condition evaluation**: Scans each bar for entry signals where ALL conditions match simultaneously.
4. **Trade simulation**: For each entry signal, enters a long position and holds for exactly N bars (configurable via `--hold`). Stop-loss exits early if price drops below the threshold.
5. **Performance metrics**: Computes total return, annualized return, Sharpe ratio, Sortino ratio, max drawdown, win rate, and risk-reward ratio.
6. **Benchmark comparison**: Runs a simple buy-and-hold strategy on the benchmark ticker for comparison.

### Known Limitations

- **Long-only**: No short selling support.
- **No transaction costs**: Assumes zero commissions or slippage.
- **Survivorship bias**: Only includes currently listed tickers.
- **Fixed hold period**: Every trade exits after exactly N bars (or earlier if stop-loss triggers).
- **AND logic only**: All conditions must match on the same bar to enter a trade.
- **Intraday data limits**: Yahoo Finance limits intraday data to 7–60 days depending on interval.

### Argument Parsing Rules

The parser expects at least two tokens: one or more tickers and an indicator name.

Optional arguments (bar_size, window, C\<count\>) can appear in any order after the indicator. The parser identifies each argument's type as follows:

1. **Bar size**: If the token (lowercased) matches one of the 13 valid intervals listed above, it is treated as the bar interval.
2. **Count**: If the lowercased token starts with `c`, it is treated as a count (`C<number>`). The part after `c` must be a positive integer.
3. **Window**: If the token is a plain positive integer, it is treated as the window.

Only one value of each type is accepted. If the input contains two bar sizes, two windows, or two count arguments, the tool prints an error and exits.

Multiple tickers are separated by commas in the first token (e.g. `AAPL,MSFT`). Spaces around commas are handled automatically — `AAPL , MSFT` is treated the same as `AAPL,MSFT`.

### Error Messages

| Condition | Message |
|-----------|---------|
| Fewer than 2 tokens | `Error: expected at least 2 values (ticker(s) indicator [bar_size] [window] [C<count>])` |
| No valid tickers after parsing | `Error: no valid tickers provided` |
| Indicator not recognised | `Error: indicator must be ADX, ATR, AV, BB, CCI, EMA, MACD, OBV, ROC, RSI, RVOL, SMA, STOCH, or VWAP` |
| Unrecognised argument (not an interval, not C-prefixed, not an integer) | `Error: unrecognised argument '<arg>'` |
| Duplicate bar size | `Error: duplicate bar size '<arg>'` |
| Duplicate window | `Error: duplicate window '<arg>'` |
| Duplicate count | `Error: duplicate count '<arg>'` |
| Invalid C-prefix (non-numeric) | `Error: invalid count '<arg>' (use C<number>, e.g. C10)` |
| Non-positive count | `Error: count must be positive` |
| Non-positive window | `Error: window must be positive` |
| Insufficient historical data for the requested window + count | `IndexError: Insufficient data for <INDICATOR>(<window>) with count=<count>` |
| Plain integer given for MACD window (not comma-separated) | `Error: MACD requires comma-separated parameters (e.g. 12,26,9)` |
| Invalid MACD params (wrong number of values, non-integer) | `Error: invalid MACD parameters '...' (use fast,slow,signal, e.g. 12,26,9)` |
| MACD fast period >= slow period | `Error: fast period (X) must be less than slow period (Y)` |
| MACD param not a positive integer | `Error: MACD parameters must be positive` |
| Plain integer given for BB (not comma-separated) | `Error: BB requires comma-separated parameters (e.g. 20,2.5)` |
| Invalid BB params (wrong number of values, non-numeric) | `Error: invalid BB parameters '...' (use window,num_std, e.g. 20,2.5)` |
| Duplicate BB parameters | `Error: duplicate BB parameters '...'` |
| BB param not a positive number | `Error: BB parameters must be positive` |
| Plain integer given for STOCH window (not comma-separated) | `Error: STOCH requires comma-separated parameters (e.g. 14,3,3)` |
| Invalid STOCH params (wrong number of values, non-integer) | `Error: invalid STOCH parameters '...' (use window,smooth_k,smooth_d, e.g. 14,3,3)` |
| Duplicate STOCH parameters | `Error: duplicate STOCH parameters '...'` |
| STOCH param not a positive integer | `Error: STOCH parameters must be positive` |
| Plain integer given for ADX window (not comma-separated) | `Error: ADX requires comma-separated parameters (e.g. 14,14)` |
| Invalid ADX params (wrong number of values, non-integer) | `Error: invalid ADX parameters '...' (use window,adx_window, e.g. 14,14)` |
| Duplicate ADX parameters | `Error: duplicate ADX parameters '...'` |
| ADX param not a positive integer | `Error: ADX parameters must be positive` |

### Examples

```bash
# Average Directional Index with default parameters (14,14)
echo "AAPL ADX" | python3 main.py

# Average Directional Index with custom DI and ADX smoothing lengths
echo "MSFT ADX 10,20 C3 1wk" | python3 main.py

# Average True Range with default window (14-day)
echo "AAPL ATR" | python3 main.py

# Average True Range with custom window and weekly bars
echo "MSFT ATR 14 1wk" | python3 main.py

# Average True Range with multiple values
echo "GOOG ATR 14 C5" | python3 main.py

# Average Volume with default window (20-day)
echo "AAPL AV" | python3 main.py

# Average Volume with custom window and weekly bars
echo "MSFT AV 10 1wk" | python3 main.py

# Bollinger Bands with default parameters (20,2.0)
echo "AAPL BB" | python3 main.py

# Bollinger Bands with custom window and standard deviations
echo "MSFT BB 20,2.5" | python3 main.py

# Bollinger Bands with count and weekly bars
echo "GOOG BB 20,2.0 C5 1wk" | python3 main.py

# Commodity Channel Index with default window (20-day)
echo "AAPL CCI" | python3 main.py

# Commodity Channel Index with custom window and weekly bars
echo "MSFT CCI 10 C5 1wk" | python3 main.py

# Custom window (50-day EMA instead of default 20)
echo "MSFT EMA 50" | python3 main.py

# MACD with default parameters (12,26,9)
echo "AAPL MACD" | python3 main.py

# MACD with custom fast, slow, and signal periods
echo "MSFT MACD 5,13,4" | python3 main.py

# MACD with count and custom bar size
echo "AAPL MACD 12,26,9 C3 1wk" | python3 main.py

# On-Balance Volume with default window (30-day history)
echo "AAPL OBV" | python3 main.py

# On-Balance Volume with custom window and weekly bars
echo "MSFT OBV 60 1wk" | python3 main.py

# Rate of Change with default window (9-day)
echo "AAPL ROC" | python3 main.py

# Rate of Change with custom window and weekly bars
echo "MSFT ROC 14 1wk" | python3 main.py

# Custom count (last 10 RSI values)
echo "AAPL RSI C10" | python3 main.py

# Multiple tickers, default values
echo "AAPL,MSFT RSI" | python3 main.py

# All optional arguments together (order does not matter)
echo "AAPL RSI 14 1mo C5" | python3 main.py

# Relative Volume with default window (10-day)
echo "AAPL RVOL" | python3 main.py

# Relative Volume with custom window and weekly bars
echo "GOOG RVOL 20 1wk" | python3 main.py

# Single ticker with default window (50-day SMA)
echo "AAPL SMA" | python3 main.py

# Custom bar size (weekly bars with 20-week SMA)
echo "GOOG SMA 20 1wk" | python3 main.py

# Intradata with a short window
echo "SPY SMA 20 5m" | python3 main.py

# Three tickers with custom window, count, and bar size
echo "AAPL,GOOG,TSLA EMA 50 C3 1wk" | python3 main.py

# Stochastic Oscillator with default parameters (14,3,3)
echo "AAPL STOCH" | python3 main.py

# Stochastic Oscillator with custom parameters
echo "MSFT STOCH 14,5,5" | python3 main.py

# Stochastic Oscillator with count and weekly bars
echo "GOOG STOCH 14,3,3 C5 1wk" | python3 main.py

# VWAP with default window (20-day)
echo "AAPL VWAP" | python3 main.py

# VWAP with custom window and weekly bars
echo "MSFT VWAP 10 1wk" | python3 main.py
```

## How It Works

The tool follows a five-step pipeline:

1. **Argument parsing**. The input line is split on whitespace. Comma-fragment tokens (e.g. `AAPL,`, `,`, `MSFT` from `AAPL , MSFT`) are merged back together. Tickers are extracted by splitting the first token on commas. The indicator is uppercased. Remaining tokens are classified as bar interval, window, or count using the rules described above. Any token that does not fit a known category triggers an error.

2. **Data period calculation**. The `_data_period()` function maps a requested window (plus the count) and bar interval to a yfinance period string. The mapping uses conservative thresholds so that enough bars are returned even after NaN rows (from the leading edge of a rolling calculation) are dropped. For example, the "1d" interval map requests "3mo" for windows up to 30 bars, "6mo" for up to 60 bars, "1y" for up to 120 bars, and so on up to "10y".

    The full `_DATA_PERIOD_MAP` for the `"1d"` interval:

    | Window ≤ | Period |
    |----------|--------|
    | 30       | 3mo    |
    | 60       | 6mo    |
    | 120      | 1y     |
    | 240      | 2y     |
    | 600      | 5y     |
    | >600     | 10y    |

    Each interval (1m, 2m, 5m, 15m, 30m, 90m, 60m, 1h, 1d, 5d, 1wk, 1mo, 3mo) has its own threshold map tuned to yfinance's data availability for that bar size.

3. **Data fetching**. `yf.Ticker(ticker).history(period=..., interval=...)` is called to retrieve a DataFrame of price data. The tool prints the number of rows received (e.g. `Fetched 252 rows for AAPL`). When multiple tickers are specified, each ticker is fetched independently with its own API call, so a failed request for one ticker does not affect the others.

4. **Indicator calculation**. For SMA, EMA, RSI, MACD, ROC, and BB the `Close` column is extracted from the DataFrame and passed to the appropriate calculation function. For VWAP, AV, RVOL, and OBV the full OHLCV DataFrame is used.  See [docs/formulas.md](docs/formulas.md) for the complete mathematical formulas.

    - **ADX**: Wilder's Directional Movement Index trio: +DI and −DI (smoothed directional movement normalised by True Range) and ADX (smoothed DX measuring trend strength regardless of direction). Bounded 0–100.
    - **ATR**: True Range (max of high−low, |high−prev close|, |low−prev close|) averaged with Wilder smoothing (`alpha = 1 / window`), measuring market volatility.
    - **AV**: Simple rolling mean of volume, following the same pattern as SMA.
    - **BB**: Three bands: middle (SMA), upper (middle + k × σ), lower (middle − k × σ). Standard deviation uses population normalisation (`ddof=0`), matching TradingView.
    - **CCI**: Typical Price `(H + L + C) / 3` compared to its SMA and normalised by 0.015 × Mean Deviation. Unbounded — values beyond ±100 flag unusual deviations.
    - **EMA**: Exponentially weighted moving average using span-based decay (`adjust=False`), giving more weight to recent prices.
    - **MACD**: Three time series: the MACD line (EMA(fast) − EMA(slow)), the signal line (EMA of the MACD line), and the histogram (MACD line − signal line).
    - **OBV**: Cumulative total that adds each bar's volume on up closes and subtracts it on down closes. Accumulation runs from the first fetched bar, so the window sets how much history is included.
    - **ROC**: Percentage change of the close over the close `window` bars ago: `(close − close[n bars ago]) / close[n bars ago] × 100`. Positive values indicate upward momentum.
    - **RSI**: Price changes are split into gains and losses. Each is averaged using Wilder smoothing (`alpha = 1 / window`), then normalised to a 0–100 range.
    - **RVOL**: Current volume divided by its rolling mean (AV). Values above 1.0 mean above-average volume; below 1.0 means below-average.
    - **SMA**: Simple rolling mean of closing prices over a configurable window.
    - **STOCH**: Stochastic Oscillator compares close to the high-low range. Raw %K is SMA-smoothed to %K, then SMA-smoothed again to %D. Bounded 0–100.
    - **VWAP**: Typical Price `(H + L + C) / 3` weighted by volume over a rolling window.

    NaN rows from the leading edge of the rolling / EWM calculation are dropped. The last `count` values of the remaining Series (or Series triple for MACD) are returned.

5. **Output formatting**. If `count=1`, a single line is printed: `TICKER WINDOW-INDICATOR: value` (for MACD: `TICKER MACD(fast,slow,signal): MACD=... Signal=... Hist=...`; for BB: `TICKER BB(window,num_std): Upper=... Middle=... Lower=...`). If `count > 1`, a header line with the ticker and range is printed, followed by one value per line.

### RSI Calculation Details

RSI uses **Wilder smoothing** (also called RMA — running moving average). This is implemented as an exponentially weighted moving average with `alpha = 1 / window` and `adjust=False`. This matches TradingView's default `ta.rsi()` function.

Because the EWM seed is set to the first value and `adjust=False`, the first row of the RSI calculation divides zero by zero and produces NaN. Every subsequent row is valid after at least one price change. This differs from the older SMA-based RSI approach, which required `window` rows of data before producing a non-NaN value.

## Project Structure

```
.
├── main.py                        # CLI entry point: parse input, dispatch
│                                  # to indicator via match/case, format
│                                  # output.  Re-exports all calculate_*
│                                  # from indicators/ for backward compat.
│
├── indicators/                    # Indicator calculation subpackage.
│   │
│   ├── __init__.py                # Re-exports all calculate_* functions.
│   │
│   ├── _data.py                   # Shared data layer: _DATA_PERIOD_MAP,
│   │                              # _VALID_INTERVALS, _DEFAULT_WINDOWS,
│   │                              # _data_period(), _fetch_close(),
│   │                              # _fetch_ohlcv().
│   │
│   ├── adx.py                     # calculate_adx()
│   ├── atr.py                     # calculate_atr()
│   ├── av.py                      # calculate_av()
│   ├── bb.py                      # calculate_bb()
│   ├── cci.py                     # calculate_cci()
│   ├── ema.py                     # calculate_ema()
│   ├── macd.py                    # calculate_macd()
│   ├── obv.py                     # calculate_obv()
│   ├── roc.py                     # calculate_roc()
│   ├── rsi.py                     # calculate_rsi()
│   ├── rvol.py                    # calculate_rvol()
│   ├── sma.py                     # calculate_sma()
│   ├── stoch.py                   # calculate_stoch()
│   └── vwap.py                    # calculate_vwap()
│
├── backtester/                     # Backtesting engine: CLI parser,
│   │                              # batch data pipeline, vectorized
│   │                              # indicators, strategy simulation,
│   │                              # financial metrics, reporting.
│   │
│   ├── __init__.py
│   ├── cli.py                     # BACKTEST command parser.
│   ├── data_pipeline.py           # Batch download + parquet cache.
│   ├── batch_indicators.py        # Vectorized indicator computation.
│   ├── engine.py                  # Core simulation loop.
│   ├── metrics.py                 # Financial metrics (Sharpe, etc.).
│   ├── reporting.py               # Console output formatting.
│   └── cache/                     # Parquet cache directory.
│
├── CHANGELOG.md                   # Version history and release notes.
│
├── run_mock_tests.py              # Runs all mock tests via pytest with a
│                                  # summary report (pass/fail counts per
│                                  # file). Uses a custom ResultCollector
│                                  # pytest plugin to capture results.
│
├── run_real_tests.py               # Runs all integration tests sequentially
│                                   # with a 1-second pause between each to
│                                   # avoid yfinance rate limits.
│
├── pytest.ini                     # Pytest configuration. Currently sets a
│                                  # filter to ignore DeprecationWarnings
│                                  # from google.protobuf (a transitive
│                                  # dependency of yfinance).
│
├── requirements.txt               # Python package dependencies.
│
├── LICENSE                        # MIT license.
│
├── MEMORY.md                      # Persistent decision and learning
│                                  # log for agent sessions.
│
├── AGENTS.md                      # Usage guide for the agent-based
│                                  # development workflow.
│
├── TODO.md                        # Planned work, priorities, and ideas
│                                  # (see docs/maintain_todo.md).
│
├── .opencode/
│   └── opencode.json              # Registers the agent personas for
│                                  # opencode (binds each to its file
│                                  # in agents/).
│
├── agents/                        # Agent personas — one file per
│   │                              # specialist role, indexed by
│   │                              # README.md and AGENTS.md.
│   │
│   ├── README.md
│   ├── task-orchestrator.md       # Routes and decomposes all work.
│   ├── idea-generator.md          # Generates and triages ideas.
│   ├── feature-implementer.md     # Writes and refactors code.
│   ├── indicator-specialist.md    # Indicator math and formulas.
│   ├── data-engineer.md           # yfinance data plumbing.
│   ├── test-engineer.md           # Authors and runs the test suites.
│   ├── code-reviewer.md           # Deep-dive architectural review.
│   ├── consistency-guardian.md    # Conventions and structure.
│   ├── documentation-expert.md    # README, docs, changelog wording.
│   ├── security-auditor.md        # Security and dependency auditing.
│   └── release-manager.md         # Versioning and release.
│
├── docs/
│   ├── adding_indicator.md        # Step-by-step process for adding
│   │                              # a new indicator to the project
│   │                              # (implementation, tests, docs).
│   │
│   ├── agent_workflows.md         # Step-by-step workflows naming the
│   │                              # agent responsible for each step.
│   │
│   ├── agents_overview.md         # Agent system model, interaction
│   │                              # graph, and assignment rules.
│   │
│   ├── code_review_guide.md       # Deep-dive architectural review
│   │                              # checklist for pre-release audits.
│   │
│   ├── commenting_guidelines.md   # Code commenting conventions used
│   │                              # throughout the project (docstring
│   │                              # style, inline comment rules).
│   │
│   ├── formulas.md                # Mathematical formulas and
│   │                              # explanations for all indicators.
│   │
│   ├── maintain_todo.md           # How to keep TODO.md up to date
│   │                              # and how it relates to other docs.
│   │
│   └── update_changelog.md        # Versioning and changelog update
│                                  # workflow for contributors.
│
├── mocktests/                     # Unit tests with mocked yfinance data.
│   │                              # The conftest.py fixture patches
│   │                              # yfinance.Ticker with a MagicMock that
│   │                              # returns a predefined DataFrame of
│   │                              # Close prices. No network calls, no
│   │                              # real market data — fast and
│   │                              # deterministic.
│   │
│   ├── conftest.py                # Factory fixture mock_stock_data().
│   │                              # Accepts a list of Close prices,
│   │                              # patches yf.Ticker, and yields the
│   │                              # mock for optional assertions.
│   │
│   ├── test_calculate_adx.py      # Tests for calculate_adx(): DI
│   │                              # dominance, trend vs choppy
│   │                              # ADX, competing movement, zero
│   │                              # range, insufficiency (added
│   │                              # in v1.6.0).
│   ├── test_calculate_atr.py      # Tests for calculate_atr(): basic
│   │                              # calculation, default window, count,
│   │                              # parameter, Wilder smoothing
│   │                              # (added in v1.3.0).
│   ├── test_calculate_av.py       # Tests for calculate_av(): basic
│   │                              # calculation, default window, count,
│   │                              # parameter, zero volume, edge cases
│   │                              # (added in v1.2.0).
│   ├── test_calculate_bb.py       # Tests for calculate_bb(): basic
│   │                              # calculation, default params, count,
│   │                              # band ordering, custom num_std.
│   ├── test_calculate_cci.py      # Tests for calculate_cci(): hand
│   │                              # computed reference values, TP
│   │                              # construction, zero deviation,
│   │                              # sign behaviour (added in
│   │                              # v1.7.0).
│   ├── test_calculate_ema.py      # Tests for calculate_ema(): basic
│   │                              # calculation, default window, count
│   │                              # parameter, insufficient data.
│   ├── test_calculate_macd.py     # Tests for calculate_macd(): basic
│   │                              # calculation, default params, count,
│   │                              # fast/slow ordering, edge cases.
│   ├── test_calculate_obv.py      # Tests for calculate_obv(): basic
│   │                              # calculation, up/down/unchanged
│   │                              # closes, zero/negative volumes,
│   │                              # insufficiency (added in v1.5.0).
│   ├── test_calculate_rsi.py      # Tests for calculate_rsi(): basic
│   │                              # calculation (Wilder reference values),
│   │                              # default window, count parameter,
│   │                              # edge cases (all same prices).
│   ├── test_calculate_roc.py      # Tests for calculate_roc(): basic
│   │                              # calculation, reference values,
│   │                              # default window, count parameter,
│   │                              # zero-denominator edge cases.
│   ├── test_calculate_rvol.py     # Tests for calculate_rvol(): basic
│   │                              # calculation, default window, count,
│   │                              # parameter, zero volume edge case
│   │                              # (added in v1.2.0).
│   ├── test_calculate_sma.py      # Tests for calculate_sma(): basic
│   │                              # calculation, default window, count
│   │                              # parameter, insufficient data.
│   ├── test_calculate_stoch.py    # Tests for calculate_stoch(): basic
│   │                              # calculation, default params, count,
│   │                              # parameter, 0-100 bounds
│   │                              # (added in v1.3.0).
│   ├── test_calculate_vwap.py     # Tests for calculate_vwap(): basic
│   │                              # calculation, default window, count,
│   │                              # parameter, zero volume, edge cases.
│   │
│   ├── test_data_period.py        # Tests for _data_period(): validates
│   │                              # every threshold in _DATA_PERIOD_MAP
│   │                              # for every interval.
│   │
│   └── test_main.py               # Tests for main(): parser dispatch,
│   │                              # default windows, C<count> syntax,
│   │                              # duplicate detection, multi-ticker
│   │                              # handling, error cases.
│
└── realtests/                     # Integration tests using the live
    │                              # yfinance API. These verify that the
    │                              # tool works end-to-end with real
    │                              # market data. Slower than mock tests
    │                              # and dependent on network availability
    │                              # and market hours.
    │
    ├── __init__.py                # Package marker.
    │
    ├── conftest.py                # Pytest hook that inserts 1-second
    │                              # spacing between real tests to avoid
    │                              # yfinance rate limits.
    │
    ├── test_calculate_adx.py      # End-to-end ADX tests with real
    │                              # data (added in v1.6.0).
    ├── test_calculate_atr.py      # End-to-end ATR tests with real data
    │                              # (added in v1.3.0).
    ├── test_calculate_av.py       # End-to-end AV tests with real data
    │                              # (added in v1.2.0).
    ├── test_calculate_bb.py       # End-to-end BB tests with real data.
    ├── test_calculate_cci.py      # End-to-end CCI tests with real data
    │                              # (added in v1.7.0).
    ├── test_calculate_ema.py      # End-to-end EMA tests with real data.
    ├── test_calculate_macd.py     # End-to-end MACD tests with real data.
    ├── test_calculate_obv.py      # End-to-end OBV tests with real data
    │                              # (added in v1.5.0).
    ├── test_calculate_rsi.py      # End-to-end RSI tests with real data.
    ├── test_calculate_roc.py      # End-to-end ROC tests with real data.
    ├── test_calculate_rvol.py     # End-to-end RVOL tests with real data
    │                              # (added in v1.2.0).
    ├── test_calculate_sma.py      # End-to-end SMA tests with real data.
    ├── test_calculate_stoch.py    # End-to-end STOCH tests with real data
    │                              # (added in v1.3.0).
    ├── test_calculate_vwap.py     # End-to-end VWAP tests with real data.
    └── test_main.py               # End-to-end CLI tests including
                                   # multi-ticker dispatch.
│
├── skills/                        # Load-on-demand skill playbooks
│   │                              # for complex workflows.
│   │
│   ├── add-indicator/
│   │   ├── SKILL.md               # Orchestrator workflow checklist.
│   │   ├── implement.md           # Code patterns for implementer.
│   │   ├── test-mock.md           # Mock test template.
│   │   └── test-real.md           # Real test template.
│   │
│   ├── release-cut/
│   │   └── SKILL.md               # Release gate sequence.
│   │
│   ├── security-audit/
│   │   └── SKILL.md               # Security scan commands.
│   │
│   └── backtester/
│       └── SKILL.md               # Backtester workflow checklist.
│
├── scripts/
│   └── verify.sh                  # Pre-handoff verification: lint,
│                                  # smoke test, full mock suite.
│
└── TODO.md                        # Planned work, priorities, and ideas
                                   # (see docs/maintain_todo.md).
```

`TODO.md` tracks planned work and ideas — see
[docs/maintain_todo.md](docs/maintain_todo.md) for how to maintain it.

## Tests

The project has two test suites: mock tests and real tests.
The **Test Engineer** agent authors and runs both suites
(see [`agents/test-engineer.md`](agents/test-engineer.md)); they are
quality gate #1 for every change.

### Mock Tests

Mock tests patch `yfinance.Ticker` so no real API calls are made. The `conftest.py` fixture creates a `MagicMock` that returns a predefined pandas DataFrame of `Close` prices. This means:

- **Deterministic** — tests always produce the same results regardless of market conditions or network availability.
- **Fast** — 521 tests run in under 1 second.
- **Comprehensive** — covers calculation logic, edge cases, parser dispatch, count behaviour, multi-ticker input, duplicate detection, and error conditions.

### Real Tests

Real tests call the live yfinance API and use whatever data it returns. They verify that the integration between the tool and Yahoo Finance actually works:

- **Reasonableness checks** — for moving-average indicators (SMA, EMA,
  VWAP, AV, BB), the result is verified to fall within the min-max range
  of its raw input data, providing a tighter, stock-specific correctness
  guarantee than a simple positive-value assertion.
- **Slower** — each test makes at least one network request.
- **Network-dependent** — fail if the machine is offline or yfinance is unreachable.
- **Time-dependent** — results may differ on weekends, holidays, or outside market hours.
- **Rate-limited** — yfinance enforces request throttling. Each real test
  takes ~1 second because a conftest hook automatically inserts 1 second of
  spacing between tests. Disable with `REALTEST_NO_SLEEP=1`.
  `run_real_tests.py` also provides spacing with per-test section headers
  and a summary report.

### Running Tests

```bash
# All mock tests (fast, no network)
python3 run_mock_tests.py

# All real tests with per-test section headers and a summary
python3 run_real_tests.py

# All tests (mock + real together)
pytest mocktests/ realtests/

# A single mock test file
pytest mocktests/test_calculate_sma.py -v

# A single real test file
pytest realtests/test_calculate_macd.py -v
```

## Agent-Based Development Workflow

QuantLab is developed through a crew of specialized agents. A single task
is rarely one agent's job — the **Task Orchestrator** assigns each task,
and each part of a task, to the agent or group of agents best equipped
for it. See [AGENTS.md](AGENTS.md) for the full usage guide,
[`docs/agent_workflows.md`](docs/agent_workflows.md) for the
step-by-step processes, and [`docs/agents_overview.md`](docs/agents_overview.md)
for the interaction model.

| Agent | Role | Assign when... | Gate when... |
|-------|------|----------------|--------------|
| Task Orchestrator | Routes and decomposes all work | Starting any multi-step task | Every handoff |
| Idea Generator | Idea generation and triage | Brainstorming, new features | An idea is ready to schedule |
| Feature Implementer | Writes and refactors code | Implementation is needed | Code must be verified |
| Indicator Specialist | Indicator math and formulas | Adding/changing indicators | Formula correctness |
| Data Engineer | yfinance data plumbing | Data layer, periods, intervals | Data robustness |
| Test Engineer | Authors and runs tests | Code needs verification | Quality gate #1 |
| Code Reviewer | Architectural review | Significant change, release | Architecture gate |
| Consistency Guardian | Conventions and structure | Style/ordering checks | Conventions gate |
| Documentation Expert | README, docs, changelog wording | Anything user-visible changes | Doc accuracy |
| Security Auditor | Security and dependency auditing | Release, dependency change | Security gate |
| Release Manager | Versioning and release | All work is done | Final release gate |
| Backtest Engineer | Backtesting engine and strategy simulation | Backtester features/fixes | Backtester correctness |

Example routing: adding a new indicator runs
`Indicator Specialist → Feature Implementer → Data Engineer → Test
Engineer → Consistency Guardian → Documentation Expert → Release
Manager`, with Code Reviewer and Security Auditor pre-release gates.
Ask the Task Orchestrator ("have the orchestrator add a new indicator")
to start any task.

## License

MIT — see `LICENSE`.
