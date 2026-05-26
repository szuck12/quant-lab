# Code Review Guide

An occasional deep-dive architectural review of the quant_indicators
codebase.  This is **not** a per-commit PR checklist — it is meant to
be run before releases, when a design question arises, or when
cross-cutting structural issues are suspected.

Cadence: before each release, or whenever the codebase undergoes
significant change (new indicator, CLI redesign, etc.).

---

## How to Use

Read through each section and examine the actual codebase.  Questions
are organised by increasing depth — start with Section 1 and stop if a
blocker is found.  Many sections ask for a judgment call rather than a
binary yes/no.

When this guide references another doc in `docs/`, read that doc first
to establish the spec, then check the codebase against it.

---

## 1. Conventions Compliance Audit

Cross-reference the actual codebase against the specifications in the
other four documentation files.

### 1a. Docstrings and Comments (commenting_guidelines.md)

- [ ] Every public function has a Google-style docstring with `Args:`,
      `Returns:`, and `Raises:` sections where applicable.
- [ ] Docstrings describe *what* and *why*, not implementation detail.
- [ ] No inline comments that restate the obvious
      (e.g. `# calculate mean`).
- [ ] 80-character line limit enforced in both code and docstrings.
- [ ] Two blank lines between all top-level functions and classes
      (PEP 8).
- [ ] One blank line between import groups (stdlib, third-party,
      local) if more than one group exists.
- [ ] Block comments used for multi-step algorithms, not single-liners.
- [ ] No stale TODO/FIXME markers left in code (checked against
      `TODO.md`).

### 1b. Type Hints (commenting_guidelines.md)

- [ ] Every function signature has type hints on all parameters and
      the return value.
- [ ] Return types accurately reflect all code paths — including
      `_return_raw` branches in indicator functions
      (e.g. `pd.Series | tuple`).
- [ ] No type information in inline comments that duplicates what
      type hints already express.

### 1c. TODO Lifecycle (maintain_todo.md)

- [ ] All entries use correct Markdown checkbox syntax:
      `- [ ]` for pending, `- [x]` for done.
- [ ] Tags are lowercase, single word, prefixed with `#`, and match
      the approved list (`#indicator`, `#test`, `#bug`, `#docs`,
      `#refactor`, `#cli`, `#infra`).
- [ ] Items in **Done** that are already recorded in a CHANGELOG
      release have been pruned.
- [ ] No item appears in two sections simultaneously.
- [ ] Open items have a clear owner or next step (not vague).

### 1d. Changelog and Versioning (update_changelog.md)

- [ ] The README version badge matches the latest CHANGELOG entry.
- [ ] The most recent version bump matches the type of change:

      | Change type | Bump | Example |
      |-------------|------|---------|
      | New indicator, new interval | MINOR | 1.1.0 → 1.2.0 |
      | Test additions, refactoring | PATCH | 1.2.0 → 1.2.1 |
      | Breaking CLI change | MAJOR | 1.x.x → 2.0.0 |

- [ ] Changelog entries include only user-facing and test-infrastructure
      changes — no internal refactoring, comment-only changes, or
      dependency bumps.
- [ ] Each entry is a single concise line from the user's perspective.
- [ ] Changelog date is accurate.

---

## 2. Indicators — Structural Audit

All eight indicator functions are expected to follow the same internal
pattern defined in `docs/adding_indicator.md` section 2a.

### 2a. Common Pattern

Walk every `calculate_*` function and check:

- [ ] Uses `_data_period(window + count, interval)` — not just
      `window` alone.
- [ ] Fetches the correct data source:

      | Indicator | Fetcher | Raw column |
      |-----------|---------|------------|
      | SMA, EMA, RSI, MACD, BB | `_fetch_close` | `Close` |
      | VWAP, AV, RVOL | `_fetch_ohlcv` | `Volume` / `(H+L+C)/3` |

- [ ] NaN rows from the leading edge of rolling/EWM calculations are
      dropped via `.dropna()` before slicing.
- [ ] Returns the last `count` values via `.iloc[-count:]`.
- [ ] Guard clause raises `IndexError` when `result.empty` or
      `len(result) < count`.
- [ ] Error message uses the canonical format:
      `f"Insufficient data for <NAME>({param}) with count={count}"`
- [ ] All eight indicators are registered in:

      - `_DEFAULT_WINDOWS` dict (line 29)
      - `main()` input prompt string (line 479)
      - `main()` validation set (line 511)
      - `main()` match/case dispatch block (line 626)

### 2b. Individual Anomalies

- [ ] **RSI**: uses Wilder smoothing (`alpha=1.0/window`). Check that
      the mock test reference value matches this formula (not SMA-based
      RSI).
- [ ] **MACD**: three return values. Is the histogram verified to equal
      `macd_line - signal_line` in tests?
- [ ] **BB**: three return values. Are upper/lower band formulas
      symmetric around middle? Does `ddof=0` match TradingView?
- [ ] **VWAP**: uses Typical Price `(H+L+C)/3`. Is there a
      reasonableness check bound on `typical`, not `close`?
- [ ] **AV**: returns `0.0` for zero-volume windows (no division).
      Does the check differ from VWAP's `IndexError` on zero volume?
- [ ] **RVOL**: window=1 produces `1.0` exactly (volume / itself).
      Is this tested?
- [ ] For functions with `_return_raw`: is the returned raw data the
      same series the indicator averages (close for SMA/EMA/BB, typical
      for VWAP, volume for AV)?

### 2c. Signature Consistency

- [ ] All functions accept `ticker, window, interval, count` in the
      same order (multi-param indicators like MACD and BB are the
      exception and accept their params before `interval`).
- [ ] Type hints match across all eight signatures.
- [ ] Default parameter values match `_DEFAULT_WINDOWS`.

---

## 3. Mock Test Coverage

Against the template in `docs/adding_indicator.md` section 3a.

### 3a. Required Categories

For each indicator test file, check:

| Category | Tests | Present for all 8? |
|----------|-------|--------------------|
| Reference test | Known-answer assertion with `pytest.approx` | |
| Window = 1 | Result equals last value | |
| Window > data length | `IndexError` or valid fallback | |
| Insufficient data | `pytest.raises(IndexError)` | |
| Constant prices | Result equals the constant | |
| Alternating pattern | Matches expected rolling value | |
| Large prices (~1e9) | No overflow | |
| Negative prices | Handled without error | |
| Spike pattern | One outlier in flat series | |
| Single price point | Works or raises correctly | |
| 20 data points | Large sequence | |
| Window near length | Edge of available data | |
| Count = 3 | Multiple values returned | |
| Count > available | `IndexError` | |
| Indicator-specific | e.g. all-gains RSI, zero-volume VWAP | |

- [ ] Are there any indicators with gaps in the above table?
- [ ] Are all 14 data sizes from the table in `adding_indicator.md`
      represented for each indicator?

### 3b. Dispatch Tests

- [ ] Each indicator has at least two tests in `mocktests/test_main.py`:

      - `test_valid_<NAME>_dispatch`: dispatches with explicit window
      - `test_default_window_<NAME>`: uses default window

- [ ] MACD and BB additionally have comma-param dispatch tests.
- [ ] Multi-ticker, C-count, interval, and error-path tests remain
      comprehensive for all indicators (not just a subset).

### 3c. Cross-Cutting Mock Concerns

- [ ] Does `mock_stock_data` supply all columns needed by every
      indicator? (VWAP/AV/RVOL need volume, VWAP needs High/Low.)
- [ ] Does any test rely on yfinance-specific behaviour that the
      mock doesn't simulate (e.g. missing columns, irregular index)?
- [ ] Is the mock's `history()` return value sufficiently realistic
      for the assertions being made?

---

## 4. Real Test Coverage and Reasonableness

Against the template in `docs/adding_indicator.md` sections 4a–4c.

### 4a. Basic Coverage

For each indicator test file:

- [ ] At least 3 different tickers (typically AAPL, MSFT, GOOG).
- [ ] At least 3 different window sizes.
- [ ] Weekly interval variant.
- [ ] Window=1 variant (where meaningful).
- [ ] Dispatch test in `realtests/test_main.py`.

### 4b. Reasonableness Checks

For each indicator, verify the check is correct:

| Indicator | Assertion | Guaranteed? |
|-----------|-----------|-------------|
| **SMA** | `close.min() <= result <= close.max()` | ✅ Mathematics of mean |
| **EMA** | `close.min() <= result <= close.max()` | ✅ Convex combination |
| **VWAP** | `typical.min() <= result <= typical.max()` | ✅ Weighted average |
| **AV** | `volume.min() <= result <= volume.max()` | ✅ Mathematics of mean |
| **BB** | `close.min() <= middle <= close.max()` | ✅ Middle band is SMA |
| **BB** | `close.iloc[-window:].std() > 0` (w>1) | ✅ Price variation |
| **RSI** | `0.0 <= result <= 100.0` | ✅ Definition |
| **MACD** | `not m.isna()`, histogram has both signs | Stock-agnostic |
| **RVOL** | `result > 0`, window=1 = 1.0 | Stock-agnostic |

- [ ] Is every assertion mathematically sound (not a heuristic)?
- [ ] Are there any remaining `result > 0.0` checks that have been
      superseded by a tighter bounds check?

### 4c. Real Test Structural Concerns

- [ ] Do any real tests make assertions that could fail due to market
      conditions (e.g. `m > 0` for MACD on a bear market ticker)?
- [ ] Are rate-limit protections adequate? (conftest 1s sleep,
      `REALTEST_NO_SLEEP` override.)
- [ ] Do the dispatch tests in `realtests/test_main.py` actually
      exercise the calculation (unlike mock dispatch tests that patch
      the function away)?

---

## 5. Error Handling and Edge Cases

Systematic sweep of every failure mode across the codebase.

### 5a. Indicator-Level Errors

- [ ] Empty data from yfinance: every indicator raises `IndexError`.
- [ ] Window > available data: every indicator raises `IndexError`
      (or handles gracefully for EMA/RSI which seed from first value).
- [ ] Count > available non-NaN rows: every indicator raises
      `IndexError`.
- [ ] All-zero price changes (RSI): raises `IndexError`.
- [ ] All-zero volume (VWAP, RVOL): raises `IndexError`.
- [ ] All-zero volume (AV): returns `0.0` — confirmed no division.
- [ ] Error messages are consistent: all use
      `f"Insufficient data for <NAME>({params}) with count={count}"`.
- [ ] No bare `except:` or `except Exception:` blocks that could
      swallow real errors.

### 5b. CLI-Level Errors

Cross-reference the README error message table against actual code:

- [ ] Fewer than 2 tokens: `sys.exit(1)` with expected message.
- [ ] No valid tickers after comma split: exit.
- [ ] Unrecognised indicator: exit with valid list.
- [ ] Unrecognised argument: exit with name of bad arg.
- [ ] Duplicate bar size / window / count: exit.
- [ ] Invalid C-prefix (non-numeric): exit.
- [ ] Non-positive window or count: exit.
- [ ] MACD: comma-separated required, fast < slow enforced,
      positive ints required.
- [ ] BB: comma-separated required, positive numbers required.
- [ ] All error messages use `sys.exit(1)` (not `raise SystemExit`
      directly, not `sys.exit(0)`).

### 5c. Data Layer Errors

- [x] yfinance unreachable: does the program handle it gracefully
      (yfinance raises its own exceptions — are they caught)?
- [ ] Unknown ticker: yfinance returns an empty DataFrame. Does
      the guard clause catch this?
- [ ] Partial data (NaN in middle of series): does rolling/EWM
      handle this, or should `.dropna()` be called pre-emptively?

---

## 6. Cross-Cutting Concerns

Issues that span multiple files or subsystems.

### 6a. Multi-Ticker Dispatch

- [ ] Each ticker gets its own yfinance call (correct — no batching).
- [x] A failure for one ticker does not prevent others from being
      calculated (each is in its own loop iteration).
- [ ] Output order matches input order.
- [ ] Comma-fragment merging handles edge cases (`AAPL , MSFT`,
      `AAPL,,MSFT`).

### 6b. Interval Handling

- [ ] All 13 intervals in `_DATA_PERIOD_MAP` are represented in
      `_VALID_INTERFALS`.
- [ ] Each interval has conservative threshold coverage in
      `test_data_period.py`.
- [ ] Real tests cover at least the `1wk` interval.
- [ ] Intraday intervals (1m, 5m, etc.) fetch enough data for
      their windows (confirmed by threshold map).

### 6c. `_return_raw` Pattern

- [ ] All five functions that have `_return_raw` return the correct
      raw data (close, typical, volume).
- [ ] No function leaks `_return_raw` through the CLI dispatch
      (no way to trigger it from stdin).
- [ ] The return type annotation is correct for both paths.
- [ ] Existing callers (CLI, mock tests, dispatch tests) are
      unaffected — none pass `_return_raw=True`.

### 6d. Print Side-Effects

- [ ] `_fetch_ohlcv` prints `Fetched N rows for TICKER` —
      does this appear in test output and cause any issues?
- [ ] Should this print be guarded by a flag or removed for tests?
- [ ] main() output formatting: ensure trailing newlines, consistent
      decimal formatting.

### 6e. Test Runner Health

- [ ] `run_mock_tests.py` correctly reports pass/fail counts.
- [ ] `run_real_tests.py` correctly discovers and serialises tests.
- [ ] conftest 1s delay still respects `REALTEST_NO_SLEEP`.
- [ ] No test file is ignored by pytest due to naming or placement.

---

## 7. Documentation Consistency

Verify that documentation matches the actual code.

### 7a. README Accuracy

- [ ] Syntax table argument descriptions match `main()` parsing
      behaviour.
- [ ] Error message table is exhaustive — no error path is missing.
- [ ] Example commands all produce valid output (spot-check 3-4).
- [ ] Project structure tree is up to date: every `.py` file in
      `mocktests/` and `realtests/` is listed.
- [ ] Version badge matches CHANGELOG.

### 7b. Cross-Reference Integrity

- [ ] All relative links between docs files work (no 404s if served).
- [ ] `docs/formulas.md` has a section for every indicator listed
      in the README, in the same order.
- [ ] `adding_indicator.md` references exist in at least one real
      test file for every pattern it describes.
- [ ] `maintain_todo.md` lifecycle is followed by `TODO.md`.
- [ ] New entries are appended at the bottom of their section, not
      inserted at the top.
- [ ] `update_changelog.md` rules are followed by `CHANGELOG.md`.

### 7c. Stale or Duplicate Content

- [ ] No section of any doc describes behaviour that was changed in a
      later version.
- [ ] No doc duplicates content from another doc (cross-reference
      instead).
- [ ] No TODO item describes something already done.

---

## 8. Open-Ended: Creative and Structural Analysis

These questions require judgment and are the heart of the review.
They have no right answer — the goal is to identify improvements and
surface design drift.

### 8a. Module Boundaries and Cohesion

`main.py` is ~260 lines encompassing:

- Imports (7 lines)
- CLI parsing + validation (~170 lines)
- Dispatch + output formatting (~80 lines)
- Entry point (2 lines)

Indicator functions and the data layer have been extracted into the
`indicators/` subpackage (one file per indicator + shared `_data.py`),
which was item 1 in the Section 8 action plan below.  main.py now
focuses solely on CLI concerns.

- If a ninth indicator were added, a new file `indicators/<name>.py`
  would be created — no changes needed to the dispatch logic beyond a
  new `case` block.
- Would extracting CLI parsing into a separate function reduce the
  cognitive load of the 170-line parser block?

### 8b. CLI Design

- Stdin-only input is unusual. What would it take to add argv support
  (`python3 main.py AAPL SMA 50`), and would that break the multi-token
  parsing?
- The comma-parameter syntax (e.g. `12,26,9`) is compact but makes
  argument classification fragile. Is there a cleaner alternative?
- Error messages are printed and the program exits. Would structured
  error output (JSON, exit codes) be useful for scripting?

### 8c. Data Period Accuracy

- `_DATA_PERIOD_MAP` has not changed since v1.0.0. Have yfinance's
  data availability guarantees changed? Are the thresholds still
  conservative enough?
- For very large windows (e.g. SMA(600) on 1d), the map requests
  `5y`. Is that always enough after NaN drops?

### 8d. Test Economics

- Real tests take ~60s with 1s sleeps. Options to improve:

  - Cache yfinance responses to disk (replay on subsequent runs)
  - Run real tests in parallel with staggered starts
  - Reduce the number of tickers (each indicator tests 3+ tickers)

- Is the 1s sleep still necessary, or has yfinance relaxed rate
  limits since v1.0.0?

### 8e. Type Safety and Static Analysis

- The project has no static type checker (mypy, pyright). Would one
  catch real bugs? Try running:

  ```bash
  pip install mypy
  mypy main.py --strict
  ```

- Would a linter (ruff, flake8) catch any of the style issues in
  Section 1a automatically?

### 8f. Dependency Risk

- `yfinance` is the sole data source. If it changes its API or is
  deprecated, the entire project becomes non-functional. Is there a
  data-source abstraction layer that could mitigate this?
- `pandas` rolling/EWM API is stable, but version-specific behaviour
  (e.g. `ddof` defaults) has changed in the past. Are minimum version
  constraints in `requirements.txt` still accurate?
- How long since the dependencies were last upgraded?

### 8g. API Surface and Versioning

- The `_return_raw` parameter is a growing pattern across indicator
  functions. Should there be a standardised protocol (e.g. a
  `compute_and_validate()` wrapper that returns `(result, metadata)`)?
- Are there other private-by-convention features that could benefit
  from standardisation?
- Would a public API doc (beyond the README) be useful for script
  consumers of the `calculate_*` functions?

### 8h. Next-Action Synthesis

Based on the findings above, produce a list of the top 3–5 actions.
Each entry must be one of two forms:

1. **Take** — a concrete action that is clearly worthwhile with no
   further debate needed (e.g. "Remove stale `test_calculate_old.py`
   from `mocktests/`").  These can be added directly to `TODO.md`.
2. **Ask** — a question that needs a decision before work proceeds
   (e.g. "Should `_fetch_ohlcv`'s print statement be routed through
   `logging.debug` instead of `print`?").  These should be raised to
   the project owner or team.

| # | Type | Action |
|---|------|--------|
| 1 | DONE | Indicator functions + data-layer helpers extracted from main.py into `indicators/` subpackage (v1.2.3). main.py is now ~260 lines focused on CLI concerns. |
| 2 | Take | Add `pandas-stubs` and run `mypy main.py --strict` in CI. The codebase already has full type hints; stubs are the only missing piece (8 false-positive errors, all from missing stubs + None tracking). |
| 3 | Take | Run `ruff check main.py` to catch the one pre-existing style issue (`l` variable name) and add ruff to `requirements.txt` / CI. |
| 4 | Ask | Should `_fetch_ohlcv`'s `print(f"Fetched {len(hist)} rows ...")` be routed through `logging.debug` instead of `print`? It appears in test output and during CLI use, which may be distracting. |
| 5 | DONE | `sys.argv` support added alongside stdin (`python3 main.py AAPL SMA 50`). Both stdin and argv work — main() accepts optional `argv` parameter, if __name__ passes sys.argv[1:] (v1.2.3). |

This guide follows the project's commenting conventions
(see `docs/commenting_guidelines.md`): 80-character line limit,
section headers, and minimal inline annotation.
