# quant_indicators

A command-line tool that fetches stock price data via [yfinance](https://github.com/ranaroussi/yfinance) and computes one of three technical indicators: Simple Moving Average (SMA), Exponential Moving Average (EMA), or Relative Strength Index (RSI). Input is provided through stdin and the result is printed to stdout. The tool is designed for quick terminal lookups — you type a ticker and an indicator, and you get back a number.

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
| `indicator` | Indicator to compute | `SMA`, `EMA`, `RSI` (case-insensitive) | Required |
| `bar_size` | Width of each price bar | `1m`, `2m`, `5m`, `15m`, `30m`, `90m`, `60m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` | `1d` |
| `window` | Lookback period in bars | Any positive integer | SMA=50, EMA=20, RSI=14 |
| `C<count>` | Number of recent values to return | `C` followed by any positive integer (e.g. `C1`, `C10`, `C100`) | `1` |

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
| Indicator not SMA, RSI, or EMA | `Error: indicator must be SMA, RSI, or EMA` |
| Unrecognised argument (not an interval, not C-prefixed, not an integer) | `Error: unrecognised argument '<arg>'` |
| Duplicate bar size | `Error: duplicate bar size '<arg>'` |
| Duplicate window | `Error: duplicate window '<arg>'` |
| Duplicate count | `Error: duplicate count '<arg>'` |
| Invalid C-prefix (non-numeric) | `Error: invalid count '<arg>' (use C<number>, e.g. C10)` |
| Non-positive count | `Error: count must be positive` |
| Non-positive window | `Error: window must be positive` |
| Insufficient historical data for the requested window + count | `IndexError: Insufficient data for <INDICATOR>(<window>) with count=<count>` |

### Examples

```bash
# Single ticker with default window (50-day SMA)
echo "AAPL SMA" | python3 main.py

# Custom window (50-day EMA instead of default 20)
echo "MSFT EMA 50" | python3 main.py

# Custom bar size (weekly bars with 20-week SMA)
echo "GOOG SMA 20 1wk" | python3 main.py

# Custom count (last 10 RSI values)
echo "AAPL RSI C10" | python3 main.py

# Multiple tickers, default values
echo "AAPL,MSFT RSI" | python3 main.py

# All optional arguments together (order does not matter)
echo "AAPL RSI 14 1mo C5" | python3 main.py

# Three tickers with custom window, count, and bar size
echo "AAPL,GOOG,TSLA EMA 50 C3 1wk" | python3 main.py

# Intradata with a short window
echo "SPY SMA 20 5m" | python3 main.py
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

4. **Indicator calculation**. The `Close` column is extracted from the DataFrame and passed to the appropriate calculation function:

    - **SMA**: `close.rolling(window=window).mean()` — simple moving average.
    - **EMA**: `close.ewm(span=window, adjust=False).mean()` — exponential moving average using the standard span-based decay.
    - **RSI**: Price changes are split into gains and losses. Each is averaged using Wilder smoothing (`ewm(alpha=1/window, adjust=False).mean()`), then the RSI is computed as `100 - (100 / (1 + avg_gain / avg_loss))`.

    NaN rows from the leading edge of the rolling / EWM calculation are dropped. The last `count` values of the remaining Series are returned.

5. **Output formatting**. If `count=1`, a single line is printed: `TICKER WINDOW-INDICATOR: value`. If `count > 1`, a header line with the ticker and range is printed, followed by one value per line.

### RSI Calculation Details

RSI uses **Wilder smoothing** (also called RMA — running moving average). This is implemented as an exponentially weighted moving average with `alpha = 1 / window` and `adjust=False`. This matches TradingView's default `ta.rsi()` function.

Because the EWM seed is set to the first value and `adjust=False`, the first row of the RSI calculation divides zero by zero and produces NaN. Every subsequent row is valid after at least one price change. This differs from the older SMA-based RSI approach, which required `window` rows of data before producing a non-NaN value.

## Project Structure

```
.
├── main.py                        # CLI entry point and all calculation logic.
│                                  # Contains: _data_period(), get_stock_data(),
│                                  # calculate_sma(), calculate_ema(),
│                                  # calculate_rsi(), and main().
│
├── run_mock_tests.py              # Runs all mock tests via pytest with a
│                                  # summary report (pass/fail counts per
│                                  # file). Uses a custom ResultCollector
│                                  # pytest plugin to capture results.
│
├── run_real_test.py               # Collects all integration tests, picks one
│                                  # at random, and runs it. Uses a
│                                  # NodeCollector plugin to enumerate test
│                                  # node IDs without running them.
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
├── docs/
│   └── commenting_guidelines.md   # Code commenting conventions used
│                                  # throughout the project (docstring
│                                  # style, inline comment rules).
│
├── mocktests/                     # Unit tests with mocked yfinance data.
│   │                              # The conftest.py fixture patches
│   │                              # main.yf.Ticker with a MagicMock that
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
│   ├── test_calculate_sma.py      # Tests for calculate_sma(): basic
│   │                              # calculation, default window, count
│   │                              # parameter, insufficient data.
│   │
│   ├── test_calculate_ema.py      # Tests for calculate_ema(): basic
│   │                              # calculation, default window, count
│   │                              # parameter, insufficient data.
│   │
│   ├── test_calculate_rsi.py      # Tests for calculate_rsi(): basic
│   │                              # calculation (Wilder reference values),
│   │                              # default window, count parameter,
│   │                              # edge cases (all same prices).
│   │
│   ├── test_data_period.py        # Tests for _data_period(): validates
│   │                              # every threshold in _DATA_PERIOD_MAP
│   │                              # for every interval.
│   │
│   ├── test_get_stock_data.py     # Tests for get_stock_data(): verifies
│   │                              # that yf.Ticker is called and
│   │                              # history() is fetched.
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
    ├── test_calculate_sma.py      # End-to-end SMA tests with real data.
    ├── test_calculate_ema.py      # End-to-end EMA tests with real data.
    ├── test_calculate_rsi.py      # End-to-end RSI tests with real data.
    ├── test_get_stock_data.py     # Tests that data is actually fetched
    │                              # from Yahoo Finance.
    └── test_main.py               # End-to-end CLI tests including
                                   # multi-ticker dispatch.
```

## Tests

The project has two test suites: mock tests and real tests.

### Mock Tests

Mock tests patch `main.yf.Ticker` so no real API calls are made. The `conftest.py` fixture creates a `MagicMock` that returns a predefined pandas DataFrame of `Close` prices. This means:

- **Deterministic** — tests always produce the same results regardless of market conditions or network availability.
- **Fast** — ~200 tests run in about 5 seconds.
- **Comprehensive** — covers calculation logic, edge cases, parser dispatch, count behaviour, multi-ticker input, duplicate detection, and error conditions.

### Real Tests

Real tests call the live yfinance API and use whatever data it returns. They verify that the integration between the tool and Yahoo Finance actually works:

- **Slower** — each test makes at least one network request.
- **Network-dependent** — fail if the machine is offline or yfinance is unreachable.
- **Time-dependent** — results may differ on weekends, holidays, or outside market hours.

### Running Tests

```bash
# All mock tests with summary report
python3 run_mock_tests.py

# One random integration test
python3 run_real_test.py

# All tests (mock + real)
pytest mocktests/ realtests/

# Only mock tests via pytest
pytest mocktests/ -v

# A single test file
pytest mocktests/test_main.py -v
```

## License

MIT — see `LICENSE`.
