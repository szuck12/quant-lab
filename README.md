# QuantLab

Current version: **3.9.0** — [Changelog](CHANGELOG.md)

Try now: [https://szuck12.github.io/quant-lab/](https://szuck12.github.io/quant-lab/)

A stock-data backtesting **web application** built with FastAPI and React.
Fetches stock price data via
[yfinance](https://github.com/ranaroussi/yfinance), computes fourteen
technical indicators, and runs multi-condition strategies across
multiple tickers with batch data download, parquet caching, and
universe scanning (S&P 500 or custom CSV).

The web application provides a form-based UI for configuring and
running backtests, with interactive equity curve charts, metrics
comparison, and trade tables.

yfinance provides access to Yahoo Finance market data. The tool does
not require an API key or account.

## Installation

Requires Python 3.12+ and Node.js 18+.

```bash
pip install -r requirements.txt
cd web && npm install
```

`requirements.txt` installs six packages:

| Package | Purpose |
|---------|---------|
| `yfinance` | Fetches stock price history from Yahoo Finance |
| `pandas` | Performs rolling window and exponential moving average calculations |
| `fastapi` | Web API framework for the backend |
| `uvicorn` | ASGI server to run the FastAPI application |
| `pydantic` | Request/response validation for API endpoints |
| `pytest` | Test runner (required for running tests) |

## Web Application

The web application provides a form-based UI for running backtests
with interactive charts and metrics.

### Starting the Web App

```bash
# Option 1: One command (starts both backend + frontend)
npm run dev

# Option 2: Two terminals
python main.py                    # Terminal 1 — backend on :8000
cd web && npm run dev             # Terminal 2 — frontend on :5173
```

Open `http://localhost:5173` in your browser.

### Web App Features

- **Three-page navigation** — Home, Backtest, and Indicators pages
  with smooth transitions and underline active indicators
- **Home page** — left-aligned hero with solid emerald accent, scrolling
  ticker tape of all indicators, equity preview chart, asymmetric feature
  grid, split-layout "How It Works", and page preview cards
- **Backtest page** — form-based UI with Quick Start example,
  interactive equity curve chart, metrics comparison, and trade tables
- **Indicators page** — 14 indicators with formulas, signals,
  parameters, usage tips, category filtering, and type-colored accents
- **Indicator selector** — choose from 14 indicators with dynamic
  parameter inputs (window, num_std, fast/slow/signal, etc.)
- **Condition builder** — add multiple conditions with AND logic
- **Equity curve chart** — strategy vs benchmark (buy-and-hold SPY)
  rendered with Recharts
- **Metrics table** — side-by-side comparison of strategy and
  benchmark (return, Sharpe, Sortino, max drawdown, win rate, etc.)
- **Trades table** — scrollable, color-coded P&L per trade
- **Legal disclaimer** — research/educational disclaimer on every page

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/indicators` | GET | Available indicators with parameter schemas |
| `/api/config` | GET | App configuration (periods, intervals) |
| `/api/backtest` | POST | Run backtest, return trades/metrics/equity curve |
| `/health` | GET | Health check |

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
├── main.py                        # Entry point: starts uvicorn web server
│
├── api/                           # FastAPI web backend.
│   │
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, CORS, router mount.
│   ├── schemas.py                 # Pydantic request/response models.
│   └── routes.py                  # Endpoints: /api/indicators, /api/periods,
│                                  # /api/backtest.
│
├── web/                           # React + TypeScript frontend.
│   │
│   ├── package.json               # Vite, React, Recharts, Tailwind CSS.
│   ├── vite.config.ts             # Vite config with Tailwind plugin and
│   │                              # API proxy to backend.
│   ├── index.html
│   └── src/
│       ├── main.tsx               # React entry point.
│       ├── App.tsx                # Main app layout.
│       ├── types.ts               # TypeScript types (mirrors api/schemas.py).
│       ├── api.ts                 # API client functions.
│       └── components/
│           ├── BacktestForm.tsx   # Form: tickers, conditions, params.
│           ├── ConditionRow.tsx   # Single condition editor.
│           ├── EquityChart.tsx    # Recharts equity curve chart.
│           ├── HomePage.tsx       # Landing page with hero, stats,
│           │                      # features, and page previews.
│           ├── IndicatorsPage.tsx  # Indicator reference with accordion.
│           ├── MetricsTable.tsx   # Strategy vs benchmark metrics.
│           ├── PageChrome.tsx     # Shared page atmosphere and separators.
│           └── TradesTable.tsx    # Scrollable trade list.
│
├── indicators/                    # Indicator calculation subpackage.
│   │
│   ├── __init__.py                # Re-exports all calculate_* functions.
│   ├── _data.py                   # Shared data layer: _DATA_PERIOD_MAP,
│   │                              # _VALID_INTERVALS, _DEFAULT_WINDOWS,
│   │                              # _data_period(), _fetch_close(),
│   │                              # _fetch_ohlcv().
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
├── backtester/                     # Backtesting engine: batch data
│   │                              # pipeline, vectorized indicators,
│   │                              # strategy simulation, financial
│   │                              # metrics, and universe scanning.
│   │
│   ├── __init__.py
│   ├── data_pipeline.py           # Batch download + parquet cache.
│   ├── batch_indicators.py        # Vectorized indicator computation.
│   ├── engine.py                  # Core simulation loop.
│   ├── metrics.py                 # Financial metrics (Sharpe, etc.).
│   ├── universe.py                # Universe resolution (S&P 500, CSV).
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
├── package.json                   # Root npm scripts: dev, build, test:api,
│                                  # test:mock, verify.
│
├── LICENSE                        # MIT license.
│
├── MEMORY.md                      # Persistent decision and learning
│                                  # log for agent sessions.
│
├── SECURITY.md                    # Security policy: supported
│                                  # versions, vulnerability reporting.
│
├── AGENTS.md                      # Usage guide for the agent-based
│                                  # development workflow.
│
├── TODO.md                        # Planned work, priorities, and ideas
│                                  # (see docs/maintain_todo.md).
│
├── .opencode/
│   └── opencode.json              # Registers the 13 agent personas for
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
│   ├── release-manager.md         # Versioning and release.
│   ├── backtest-engineer.md       # Backtesting engine and simulation.
│   └── web-developer.md           # FastAPI backend + React frontend.
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
│   ├── conventions_reference.md   # Shared conventions reference (§1–§19).
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
│   ├── test_api.py                # FastAPI endpoint tests: indicators,
│   │                              # periods, backtest, validation,
│   │                              # error handling (17 tests).
│   │
│   ├── test_backtester.py         # Backtester tests: conditions,
│   │                              # simulation, metrics, data pipeline,
│   │                              # errors, universe integration.
│   │
│   ├── test_data_period.py        # Tests for _data_period(): validates
│   │                              # every threshold in _DATA_PERIOD_MAP
│   │                              # for every interval.
│   │
│   └── test_universe.py           # Universe module tests: S&P 500
│                                  # resolution, CSV loading, caching,
│                                  # scraping fallback (25 tests).
│
├── realtests/                     # Integration tests using the live
│   │                              # yfinance API. These verify that the
│   │                              # tool works end-to-end with real
│   │                              # market data. Slower than mock tests
│   │                              # and dependent on network availability
│   │                              # and market hours.
│   │
│   ├── __init__.py                # Package marker.
│   │
│   ├── conftest.py                # Pytest hook that inserts 1-second
│   │                              # spacing between real tests to avoid
│   │                              # yfinance rate limits.
│   │
│   ├── test_calculate_adx.py      # End-to-end ADX tests with real
│   │                              # data (added in v1.6.0).
│   ├── test_calculate_atr.py      # End-to-end ATR tests with real data
│   │                              # (added in v1.3.0).
│   ├── test_calculate_av.py       # End-to-end AV tests with real data
│   │                              # (added in v1.2.0).
│   ├── test_calculate_bb.py       # End-to-end BB tests with real data.
│   ├── test_calculate_cci.py      # End-to-end CCI tests with real data
│   │                              # (added in v1.7.0).
│   ├── test_calculate_ema.py      # End-to-end EMA tests with real data.
│   ├── test_calculate_macd.py     # End-to-end MACD tests with real data.
│   ├── test_calculate_obv.py      # End-to-end OBV tests with real data
│   │                              # (added in v1.5.0).
│   ├── test_calculate_rsi.py      # End-to-end RSI tests with real data.
│   ├── test_calculate_roc.py      # End-to-end ROC tests with real data.
│   ├── test_calculate_rvol.py     # End-to-end RVOL tests with real data
│   │                              # (added in v1.2.0).
│   ├── test_calculate_sma.py      # End-to-end SMA tests with real data.
│   ├── test_calculate_stoch.py    # End-to-end STOCH tests with real data
│   │                              # (added in v1.3.0).
│   └── test_calculate_vwap.py     # End-to-end VWAP tests with real data.
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
│   ├── backtester/
│   │   └── SKILL.md               # Backtester workflow checklist.
│   │
│   └── webapp/
│       └── SKILL.md               # Web app workflow checklist.
│
├── scripts/
│   └── verify.sh                  # Pre-handoff verification: lint,
│                                  # smoke test, API tests, frontend
│                                  # build, full mock suite.
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
- **Fast** — 671 tests run in under 2 seconds.
- **Comprehensive** — covers calculation logic, edge cases, parser dispatch, count behaviour, multi-ticker input, duplicate detection, error conditions, API endpoints, and universe scanning.

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
| Web Developer | React frontend + FastAPI backend | Web app features/fixes | Web app correctness |

Example routing: adding a new indicator runs
`Indicator Specialist → Feature Implementer → Data Engineer → Test
Engineer → Consistency Guardian → Documentation Expert → Release
Manager`, with Code Reviewer and Security Auditor pre-release gates.
Adding a web app feature runs `Web Developer → Test Engineer →
Consistency Guardian → Documentation Expert → Release Manager`.
Ask the Task Orchestrator ("have the orchestrator add a new indicator")
to start any task.

## Deployment

The web application is deployed as two services:

| Service | Host | URL |
|---------|------|-----|
| Frontend | GitHub Pages | https://szuck12.github.io/quant-lab/ |
| Backend | Render.com | https://quant-lab-api.onrender.com |

### How It Works

The frontend is a static React build served by GitHub Pages. The
backend is a Python FastAPI service running on Render.com. The
frontend calls the backend API over HTTPS for backtest execution
and indicator metadata.

### Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `VITE_API_URL` | Frontend build | Backend URL for API calls |

In local development, `VITE_API_URL` is not set and the Vite proxy
handles API routing. In production, it is set to the Render backend URL.

### Backend Health Check

The backend exposes `GET /health` which returns `{"status": "ok"}`.
This is used by Render for health checks and availability monitoring.

## License

MIT — see `LICENSE`.
