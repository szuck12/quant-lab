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
- **2026-08-31**: v3.0.0 — web application. CLI replaced by FastAPI
  backend + React/Vite/TypeScript frontend. Backend: `api/` package
  with Pydantic models and 3 endpoints (`/api/indicators`,
  `/api/periods`, `/api/backtest`). Frontend: React 19, Tailwind CSS
  v4, Recharts for equity curve charts. Dynamic indicator params
  rendered from API schema. Period selector (1mo–20yr). Metrics table
  with strategy vs benchmark comparison. Trades table with color-coded
  P&L. CORS for Vite dev server. NaN sanitization in equity curve.
  Legacy CLI preserved: `python main.py backtest <args>`. 17 API tests.
  13 agents total (11 original + backtest-engineer + web-developer).
  New skill: `skills/webapp/`. conventions_reference.md §19 added.
- **2026-08-31**: v3.1.0 — simplified UI + robustness. Removed ticker
  input, simplified form to "Last N years" + "Initial Capital". Added
  indicator param hints and value range guidance. New `/api/config`
  endpoint. Engine handles universe internally. Added error banner for
  failed API fetches. 22 API tests, 669 total mock tests passing.
- **2026-08-31**: v3.2.0 — comprehensive UI/UX revamp. Typography:
  Space Grotesk for display, Inter for body, JetBrains Mono for code.
  Colors: emerald + cyan + purple accents on slate background with
  dot grid texture. Indicators page: expanded with type badges,
  interpretation, bullish/bearish signals, parameters, best-for,
  similar indicators, pro tips, formulas. Category filtering
  (Momentum/Trend/Volatility/Volume). Backtest page: "How It Works"
  3-step guide, "Why QuantLab" feature grid, Quick Start example
  with one-click RSI demo, results summary cards. Micro-interactions:
  card hover effects, gradient text, glass morphism nav. All 671
  tests passing.
- **2026-08-31**: v3.3.0 — three-page structure + rich animations.
  New Home page with hero section, animated counters, floating
  particles, page previews, and open source banner. Navigation
  redesigned with gradient active states and version badge. Bug
  fixes: VWAP type changed from 'Other' to 'Volume', similar
  indicators filtered to only project indicators, Expand All/
  Collapse All fixed. Added rose (#F43F5E) as 4th accent color.
  Rich animations: floating dots, gradient rotation, stagger-fade-in,
  page transitions, glow hover effects. Typography consistency
  improved across all components. All 671 tests passing.

## Corrections & Lessons Learned

<!-- Record mistakes and what was learned from them. -->

- **File naming**: `documentation-expect.md` was a typo for
  `documentation-expert.md`. Always verify agent filenames before
  committing.
- **JSON permissions**: opencode.json agent permission objects must use
  the last-match-wins pattern (`"*": "ask"` first, specific allows
  last) to avoid global allow overriding specific deny.
- **NaN in JSON**: Pydantic models with `float` fields will serialize
  NaN values to JSON, causing `ValueError`. Always sanitize equity
  curve data by replacing NaN with the capital value before returning
  from API endpoints.
- **`import type` in TypeScript**: When `verbatimModuleSyntax` is
  enabled in tsconfig, type-only imports must use `import type` syntax.
  Apply this to all TypeScript files that import interfaces/types.
- **Port 8000 conflict**: If another application is already running on
  port 8000, the QuantLab API will fail with 404. Always check for
  port conflicts before starting: `lsof -i :8000`. Kill conflicting
  processes with `kill <PID>` before starting the backend.
- **Silent fetch failures**: Frontend API calls that fail silently
  (`.catch(console.error)`) make debugging impossible. Always add
  visible error state in React components for critical data fetches.

## Last Session State

<!-- Brief snapshot of where work left off. Updated at end of session. -->

- Current version: 3.3.0
- All 671 mock tests passing (24 API + 197 backtester + 25 universe +
  12 integration + 413 indicator tests).
- 13 agents total (11 original + backtest-engineer + web-developer).
- Web app: FastAPI backend on `:8000`, React/Vite frontend on `:5173`.
- Vite proxies `/api` to backend in dev mode.
- `npm run dev` starts both backend and frontend concurrently.
- Legacy CLI: `python main.py backtest <args>`.
- Indicator CLI preserved in `cli.py` (imported by test_main.py).
- `indicators/` package kept for web use (not deleted).
- Shared conventions: `docs/conventions_reference.md` §1–§19.
- Skills: `add-indicator/`, `release-cut/`, `security-audit/`,
  `backtester/`, `webapp/`.
- All agent files updated with web app constraints.
- README updated for v3.3.0: three-page structure, rich animations.
- docs/agents_overview.md: thirteen agents, updated roster.
- docs/agent_workflows.md: Workflow I (web app), updated graph, web verify cmds.
- agents/README.md: 13-agent roster.
- Root `package.json` with `npm run dev` for concurrent startup.
- Data file: `web/src/data/indicators.ts` (14 indicators with
  full descriptions, signals, parameters, tips, formulas).
- Design system: Space Grotesk (display) + Inter (body) + JetBrains Mono (code).
- Colors: emerald + cyan + purple + rose accents, dot grid background.
- Three-page structure: Home, Backtest, Indicators.
- Home page: hero, animated counters, floating particles, page previews.
- Indicators page: category filtering, type badges, expanded content.
- Backtest page: Quick Start example, results summary cards.
- Rich animations: float, gradient-rotate, stagger-fade-in, page-in.
