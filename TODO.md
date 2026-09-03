# TODO

## In Progress


## Done

- [x] 2026-09-01 — v3.5.0 — Round 2 visual refinements: node-graph
      favicon/logo, mini equity chart preview, color-coded ticker tape,
      constellation dots, gradient blob, typing animation, pulse badge,
      section dividers, scroll-stagger animations, smart expand/collapse,
      3-section formula, indicator glow, disclaimer redesign, backtest
      header, corrected indicator list, fixed CLI commands (#design, @web-developer)
- [x] 2026-09-01 — v3.4.0 — de-AI web redesign: custom sigma favicon,
      solid emerald palette, left-aligned hero, asymmetric feature grid,
      scrolling ticker tape, terminal preview, noise texture, math symbol
      decorations, type-colored indicator accents, expand/collapse fix,
      legal disclaimer (#design, @web-developer)
- [x] 2026-08-31 — v3.0.0 web application: FastAPI backend +
      React/Vite/TypeScript frontend, 17 API tests, web-developer
      agent, webapp skill, updated docs
      (#feature, @web-developer @test-engineer @documentation-expert)
- [x] 2026-08-31 — Universe/scanner feature: `--universe sp500` or
      CSV, `--max-tickers N`, chunked download, summary reporting
      (#feature, @backtest-engineer @data-engineer @test-engineer)
- [x] 2026-08-15 — Implement Commodity Channel Index (CCI) indicator (#indicator)
- [x] 2026-07-05 — Implement Average Directional Index (ADX) indicator (#indicator)
- [x] 2026-06-19 — Implement On-Balance Volume (OBV) indicator (#indicator)
- [x] 2026-06-16 — Implement Rate of Change (ROC) indicator (#indicator)
- [x] 2026-05-27 — Implement Stochastic Oscillator (STOCH) indicator (#indicator)
- [x] 2026-05-27 — Implement Average True Range (ATR) indicator (#indicator)
- [x] 2026-05-25 — Split indicator functions from main.py into indicators/
      subpackage (#refactor)
- [x] Fix realtest conftest 1s delay applying to mock tests when running
      `pytest mocktests/ realtests/` together (#test, #bug)
- [x] 2026-09-02 — v3.7.0 — position sizing: Portfolio class, position
      size (total/unallocated), repeat-ticker logic, position-weighted
      returns, cash/positions in API response, frontend controls,
      comprehensive tests (#feature, @backtest-engineer @web-developer)
- [x] 2026-09-01 — v3.6.1 — replaced GitHub Actions keep-alive cron
      (throttled) with cron-job.org external scheduler (#deploy,
      @web-developer)
- [x] 2026-09-01 — v3.6.0 — public deployment: Render.com backend,
      GitHub Pages frontend, Dockerfile, env-based API URL, auto-deploy
      workflows (#deploy, @web-developer)
- [x] 2026-09-01 — v3.5.1 — shared page atmosphere, continuous ticker,
      compact labeled hero chart, footer disclaimer consolidation, stable
      headline wrapping, animated 100% counter, backtest dark accents,
      calmer indicator hover, explicit VWAP rail, and formula color fixes
      (#bug, @web-developer)

## High Priority

(Important changes that should be done soon.)

- [ ] 2026-08-22 — Evaluate merging open Dependabot PRs (yfinance 1.x,
      pandas 3.x): add CI for automated test runs first, then verify
      with full mock + real suites before merging
      (#deps, @security-auditor @test-engineer @feature-implementer
      @release-manager)

## Medium Priority

(Should get done, not urgent.)

- [ ] Test MACD accuracy against known reference values
      (#indicator, #test, @test-engineer @indicator-specialist)
- [ ] Test BB accuracy against known reference values
      (#indicator, #test, @test-engineer @indicator-specialist)
- [ ] Improve structure of MACD and BB indicator output
      (#indicator, @feature-implementer)

## Low Priority

(Nice-to-haves.)

## Ideas

(Interesting ideas not yet committed to implementation.)

- [ ] Allow multiple indicators in a single backtest run (web + CLI)
      (#feature, @idea-generator)
