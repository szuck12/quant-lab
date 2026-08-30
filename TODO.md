# TODO

## In Progress


## Done

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
      (#cli, @feature-implementer)

## Low Priority

(Nice-to-haves.)

## Ideas

(Interesting ideas not yet committed to implementation.)

- [ ] Allow multiple indicators to be calculated in a single command-line
      input (#cli, @idea-generator)
