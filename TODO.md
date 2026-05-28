# TODO

## In Progress


## Done

- [x] 2026-05-27 — Implement Stochastic Oscillator (STOCH) indicator (#indicator)
- [x] 2026-05-27 — Implement Average True Range (ATR) indicator (#indicator)
- [x] 2026-05-25 — Split indicator functions from main.py into indicators/
      subpackage (#refactor)
- [x] Fix realtest conftest 1s delay applying to mock tests when running
      `pytest mocktests/ realtests/` together (#test, #bug)

## High Priority

(Important changes that should be done soon.)

## Medium Priority

(Should get done, not urgent.)

- [ ] Test MACD accuracy against known reference values (#indicator, #test)
- [ ] Test BB accuracy against known reference values (#indicator, #test)
- [ ] Improve structure of MACD and BB indicator output (#cli)

## Low Priority

(Nice-to-haves.)

## Ideas

(Interesting ideas not yet committed to implementation.)

- [ ] Allow multiple indicators to be calculated in a single command-line
      input (#cli)
