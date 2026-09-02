# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com) and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.6.0] - 2026-09-01

### Added
- **Public deployment** — backend hosted on Render.com (free tier),
  frontend on GitHub Pages. Fully functional backtest engine available
  at https://szuck12.github.io/quant-lab/.
- **Environment-based API URL** — frontend uses `VITE_API_URL` env var
  to switch between local dev proxy and production backend.
- **GitHub Pages base path** — Vite build configured with `/quant-lab/`
  base for correct asset paths.
- **Backend Dockerfile** — containerized Python backend for Render
  deployment.
- **Live demo link** — clickable link to the deployed website in README.
- **CORS tests** — added tests verifying GitHub Pages and localhost
  origins are allowed, and unknown origins are rejected.
- **Deployment verification** — added Dockerfile and GitHub Actions
  checks to the pre-handoff verification script.

### Changed
- **Page atmosphere** — fixed background stretching by constraining
  constellation SVG to minimum viewport height instead of scaling
  with page content length.
- **Background replaced** — removed constellation dots, gradient blob,
  and noise texture. Replaced with a subtle CSS dot grid pattern
  (pure CSS, resolution-independent, zero HTTP requests).

## [3.5.1] - 2026-09-01

### Changed
- **Main-page atmosphere** — extended the subtle gradient, constellation,
  and texture treatment across the Home, Backtest, and Indicators bodies,
  while keeping the footer separate.
- **Footer layout** — placed the legal disclaimer directly beneath the
  version and Free & Open Source copy in one coherent footer section.
- **Backtest styling** — added darker navy accents and meaningful line-only
  separators while preserving the existing light form surfaces.
- **Headline and statistics** — kept "Indicators" on a stable second line
  during typing and animated the 100% Free counter.
- **Indicator reference styling** — reduced hover brightness, added top
  spacing to expanded content, made the Volume rail explicit for VWAP,
  and aligned formula headers to emerald, cyan, and purple.

### Fixed
- **Ticker carousel** — made the indicator marquee loop continuously with
  identical repeated groups and removed the scanning light effect.
- **Hero chart** — added compact period and currency axes and constrained
  the plot to a narrower centered width.
- **Homepage cleanup** — removed the indicators pulse dot, stray triangle,
  and confusing formula text from decorative separators.

## [3.5.0] - 2026-09-01

### Added
- **Node-graph favicon/logo** — abstract diamond-shaped node graph with
  4 colored dots connected by lines, replacing the sigma mark that
  resembled the letter "Z". Non-letter abstract shape.
- **Mini equity chart preview** — hero section now shows a Recharts
  AreaChart with an upward-trending equity curve and 3 metric chips
  (+24.7% Return, 1.41 Sharpe, 62.3% Win Rate), replacing the static
  terminal code block.
- **Color-coded ticker tape dots** — each indicator name's dot is now
  colored by its type: emerald (Momentum), cyan (Trend), amber
  (Volatility), rose (Volume).
- **Constellation dot grid** — subtle SVG overlay in the hero background
  with small drifting dots and faint connecting lines, creating a
  data-network visualization.
- **Hero gradient blob** — large, soft emerald radial gradient blob
  that slowly drifts position behind the hero text using CSS animation.
- **Hero typing animation** — headline "Backtest Technical Indicators"
  types in letter by letter with a blinking cursor on first load.
- **Live indicator pulse badge** — pulsing green dot next to the "14
  Indicators" stat suggesting the platform is active.
- **Section dividers with formula fragments** — thin gradient lines
  between major sections with faint math symbols (sigma, alpha, beta,
  etc.) as decorative breaks reinforcing the quantitative theme.
- **Scroll-triggered stagger animations** — elements fade in from below
  with staggered delays as their parent section enters the viewport,
  using IntersectionObserver.
- **Smart expand/collapse toggle** — button now shows "Expand All" when
  fewer than half of indicators are open, "Collapse All" when more than
  half are open, derived from actual open count rather than a boolean.
- **3-part formula section** — indicator accordions now show Formula
  (expanded from docs/formulas.md), Components (symbol-by-symbol
  explanations), and Breakdown (verbal description), replacing the
  previous 2-part layout.
- **Indicator card glow effect** — hover over any indicator accordion
  to see a subtle type-colored glow shadow (emerald for Momentum, cyan
  for Trend, etc.).
- **Version badge** — "v3.5.0" displayed in the nav header and footer.
- **Backtest page header** — matching accent line, heading, and
  subtitle consistent with the Indicators page design.

### Changed
- **"100%" stat color** — changed from `text-slate-700` to
  `text-purple-600` for visual distinction.
- **How It Works steps** — increased step number circle size (h-10 to
  h-12), added vertical connecting gradient line between steps, added
  left accent border on hover with background tint.
- **Indicator tags** — shrunk from `text-[10px] px-2` to `text-[9px]
  px-1.5` and corrected list to exactly match the 14 project indicators.
- **Open Source CLI commands** — corrected to match actual README
  (pip install, cd web && npm install, npm run dev).
- **Disclaimer section** — redesigned with heading, dark navy-950
  background, left-aligned text, emerald accent line, and increased
  padding. Visually distinct from footer.
- **Backtest button** — replaced gradient button with solid emerald-600.
- **Ticker tape indicator list** — fixed to exactly 14 project
  indicators (removed Williams %R, MFI, Parabolic SAR, Ichimoku Cloud).
- **Em dashes removed** — all em dashes in indicator data replaced
  with commas or semicolons.
- **Formula expansion** — all 14 indicator formulas expanded to match
  full mathematical representation from docs/formulas.md.
- **Formula Components** — new `formulaComponents` field added to
  IndicatorData interface with pipe-delimited symbol explanations.

### Removed
- **Terminal preview** — static CLI code block replaced by mini equity
  chart and metrics preview.
- **Gradient button** — backtest "Run Backtest" button no longer uses
  emerald-cyan-purple gradient.

## [3.4.0] - 2026-09-01

### Added
- **Custom favicon** — sigma/node-graph SVG mark in emerald, replacing
  the default Vite lightning bolt.
- **Scrolling ticker tape** — horizontal marquee of all 14 indicator
  names below the hero section, animating continuously.
- **Terminal preview** — mock CLI output block on the homepage showing
  realistic quantlab commands and results, giving a tool-first feel.
- **Split-layout "How It Works"** — asymmetric two-column section with
  text on the left (2/5) and stepped process cards on the right (3/5),
  breaking the centered three-step AI pattern.
- **Asymmetric feature grid** — "Why QuantLab" redesigned as a 2/3 + 1/3
  grid: one large card with full indicator list, two smaller cards for
  speed and open source. Cards use left-edge accent sweep on hover.
- **Left-edge accent hover** — new `.card-accent-hover` animation that
  reveals a colored left border on hover, replacing generic translateY lift.
- **Noise texture overlay** — subtle SVG noise filter applied to body for
  a tactile, printed-paper feel. Breaks the flat digital look.
- **Decorative math symbols** — sigma, delta, mu characters scattered as
  faint background elements, reinforcing the quantitative theme.
- **Large display numbers** — `.display-number` utility for oversized stats
  with tight tracking and tabular numerals.
- **Legal disclaimer** — research/educational disclaimer below the footer
  on every page, clarifying QuantLab is not a broker or advisor.
- **Type-colored indicator accents** — each accordion item on the Indicators
  page now has a left border colored by type (emerald=Momentum, cyan=Trend,
  amber=Volatility, rose=Volume).
- **Color-coded filter tabs** — active indicator type tab now uses the
  type's own color instead of generic slate-800.
- **Solid nav underline indicator** — active page shows a 2px emerald
  underline instead of gradient pill background.
- **Left-aligned hero** — homepage hero is now left-aligned with a mono
  label ("QUANTITATIVE RESEARCH PLATFORM") instead of centered gradient text.

### Changed
- **Favicon** — replaced purple Vite lightning bolt with custom sigma mark.
- **Navigation logo** — replaced gradient "Q" box with inline SVG sigma mark.
- **Hero text** — replaced gradient rainbow text with solid emerald color.
- **Stats section** — removed "500+ S&P 500 Stocks" and "671+ Tests
  Passing"; replaced with "1M+ Indicator Combinations" and "100% Free".
  Reduced from 4-column to 3-column grid.
- **Button styles** — replaced all gradient buttons with solid-color buttons
  (emerald-600 primary, white secondary).
- **Nav active states** — replaced gradient pill background with solid
  underline indicator.
- **Background** — replaced dot-grid radial gradient with warm off-white
  (#FAFAF8) + subtle noise texture.
- **Border radius** — reduced from `rounded-2xl` (16px) to `rounded-xl`
  (12px) on cards, `rounded-lg` (8px) on buttons. No longer uniform.
- **Animations trimmed** — removed floating dots, gradient-rotate, shimmer,
  pulse-glow, subtle-pulse, ticker (replaced with new ticker), stagger
  beyond 3 steps. Kept: fade-in, page-in, count-up, ticker, blink.
- **Glass morphism removed** — nav uses solid `bg-white/95` with border
  instead of `backdrop-blur` translucent glass.
- **Footer** — simplified, version text removed from footer display.
- **Indicators page header** — applied `font-display` to h1 and indicator
  names. Added emerald accent line below title.
- **Formula block** — improved with colored section headers (emerald for
  Formula, cyan for Breakdown).

### Fixed
- **Expand All / Collapse All bug** — moved per-indicator open state from
  local component to parent `IndicatorsPage` as a `Set<string>`. Individual
  accordion clicks now properly clear the expand-all flag, preventing state
  conflicts when mixing manual and bulk toggles.

## [3.3.0] - 2026-08-31

### Added
- **Home page** — new landing page with hero section, animated
  counters, floating particles, and page previews.
- **Three-page navigation** — Home, Backtest, and Indicators pages
  with dedicated routes and smooth transitions.
- **Animated counters** — number count-up animations on stats
  section showing S&P 500 stocks, indicators, tests, and cost.
- **Floating particles** — subtle animated dots in hero section
  for visual depth and movement.
- **Page previews** — interactive cards linking to Backtest and
  Indicators pages with hover effects.
- **Open source banner** — dedicated section with GitHub link
  and call-to-action.
- **Gradient nav pills** — active page shows gradient background
  instead of flat color.
- **Version badge** — v3.3.0 badge in navigation header.
- **Rich animations** — float, gradient-rotate, ticker, count-up,
  stagger-fade-in, page-in, subtle-pulse animations.
- **Glow hover effects** — emerald and cyan glow on button hover.
- **Rose accent color** — added rose (#F43F5E) as 4th accent
  color for warnings and negative values.

### Fixed
- **VWAP indicator type** — changed from 'Other' to 'Volume' to
  properly categorize the indicator.
- **Similar indicators filtering** — updated all 14 indicators
  to only reference other project indicators (removed Aroon,
  Chaikin ADX, DEMA, TEMA, Williams %R, Keltner Channels,
  Donchian Channels, Volume Profile, TWAP, Momentum, WMA,
  Chaikin Money Flow, Volume Price Trend, Historical Volatility).
- **Expand All/Collapse All** — fixed accordion functionality
  by passing expandAll prop to child components and using
  effectiveIsOpen state.
- **Error styling** — updated error messages to use rose color
  instead of red for consistency.

### Changed
- **Typography consistency** — applied font-display (Space Grotesk)
  to all headings across components.
- **Color palette** — added rose color and applied more broadly
  for negative values and warnings.
- **Navigation design** — gradient active state, version badge,
  and hover transitions.
- **Removed 'Other' type** — eliminated 'Other' from IndicatorType
  union and TYPE_COLORS since all indicators now have proper types.

## [3.2.0] - 2026-08-31

### Added
- **Indicators reference page** — new page with all 14 indicators
  showing descriptions, interpretation, bullish/bearish signals,
  parameters, formulas, and usage tips.
- **Category filtering** — filter indicators by type (Momentum,
  Trend, Volatility, Volume) with count badges.
- **Indicator type badges** — colored badges showing indicator
  category on both pages.
- **"How It Works" section** — 3-step visual guide explaining
  the backtesting process.
- **"Why QuantLab" feature grid** — 6 feature cards highlighting
  key capabilities (speed, indicators, control, coverage, access,
  open source).
- **Quick Start example** — collapsible section with pre-filled
  RSI oversold example and one-click "Try this example" button.
- **Results summary cards** — 4 large metric cards above the chart
  showing Total Return, Sharpe Ratio, Win Rate, and Total Trades.
- **Space Grotesk font** — distinctive display font for headlines
  and headings.
- **Dot grid background** — subtle texture for visual depth.
- **Gradient text** — emerald-to-cyan gradient for accent text.
- **Card hover effects** — subtle lift and shadow on card hover.
- **Staggered animations** — fade-in animations for content sections.

### Changed
- **Color palette expanded** — added purple as tertiary accent
  alongside emerald and cyan.
- **Typography hierarchy** — Space Grotesk for display, Inter for
  body, JetBrains Mono for code/data.
- **Card styling** — updated to use rounded-2xl and subtle borders.
- **Form labels** — using Space Grotesk font for consistency.
- **Navigation** — using Space Grotesk for brand name.

### Removed
- **Internal note from indicators page** — moved to internal
  documentation only (webapp skill).

## [3.1.0] - 2026-08-31

### Added
- **Simplified UI** — removed ticker input; auto-uses S&P 500
  universe via engine's `config["universe"]`.
- **"Last N years" input** — replaced period dropdown with numeric
  input (1–20 years).
- **Initial Capital input** — simplified capital entry.
- **Indicator param hints** — `hint` field on parameter schemas
  shows purpose (e.g. "Lookback period").
- **Value range guidance** — `value_hint` field on indicators shows
  expected value ranges (e.g. "0–100 (30 = oversold, 70 = overbought)").
- **`GET /api/config`** — returns `max_years` and defaults for
  form initialization.
- **Error banner** — visible error state when API fetches fail
  (e.g. "Failed to load indicators. Is the backend server running?").
- **Client-side validation** — years (1–max) and capital (positive,
  ≤$1B) validated before submission.
- **Server-side validation** — years and capital validated with
  clear error messages.
- **NaN/Infinity handling** — MetricsTable shows "—" for invalid
  numeric values.
- **Empty trades state** — TradesTable shows helpful message when
  no trades match conditions.
- **Frontend integration tests** — 2 new tests verify API responses
  match TypeScript interfaces.

### Changed
- **`BacktestRequest` simplified** — now only takes `conditions`,
  `capital`, `years` (removed tickers, hold, benchmark, stop_loss).
- **Engine handles universe** — `BacktestEngine` resolves universe
  internally via `config["universe"]`; route does NOT call
  `resolve_universe` directly.
- **`GET /api/periods` replaced** — now `GET /api/config` returns
  `max_years` instead of period options.
- **Form simplified** — removed hold, benchmark, stop_loss inputs
  from top-level form.

### Fixed
- **Silent fetch failures** — frontend now shows visible error
  banner when API calls fail (was `.catch(console.error)`).
- **Port 8000 conflict** — documented in MEMORY.md and agent docs;
  `lsof -i :8000` check added to webapp skill and web-developer
  agent tools.

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
- **`cli.py` extracted** — legacy indicator CLI moved to standalone
  `cli.py` at repo root (backward-compatible import for tests).
- **`requirements.txt`** — added `fastapi`, `uvicorn[standard]`,
  `pydantic`.
- **`.gitignore`** — added `web/node_modules/` and `web/dist/`.
- **`AGENTS.md`** — added Web Developer to roster, routing,
  file ownership, and skills index.
- **`MEMORY.md`** — v3.0.0 web application decisions logged.
- **Root `package.json`** — added `npm run dev` for concurrent
  backend + frontend startup.
- **Total mock tests** — 664 tests (17 API + 197 backtester +
  25 universe + 12 integration + 413 indicator).

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
