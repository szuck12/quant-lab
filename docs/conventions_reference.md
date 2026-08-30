# Conventions Reference

Single source of truth for conventions enforced across QuantLab. Agent
files reference this file; the specifics they enforce are listed in
their Standards Enforced sections.

## 1. Code Style

- **Line limit**: 80 characters in code and docstrings.
- **PEP 8 spacing**: two blank lines between top-level functions and
  classes, one blank line between import groups (stdlib, third-party,
  local).
- **Docstrings**: Google-style with `Args:`, `Returns:`, `Raises:`
  sections. Describe what and why, never how.
- **Type hints**: every function signature must have type annotations.
- **Comments**: why, not what. No obvious-obvious comments (e.g.
  `# calculate mean`).
- **Module header**: every `.py` file starts with a brief comment
  describing the module purpose (e.g. `# indicators/sma.py`).

## 2. Alphabetical Ordering

These lists, dicts, and structures must be in strict alphabetical
order:

1. `indicators/__init__.py` imports.
2. `main.py` imports (same order as `__init__.py`).
3. `main.py` input prompt — indicator names listed alphabetically.
4. `main.py` validation set — `("ADX", "ATR", ...)` in order.
5. `main.py` `match/case` dispatch — cases in alphabetical order.
6. `indicators/_data.py` `_DEFAULT_WINDOWS` — entries in order.
7. `docs/formulas.md` sections — alphabetical by indicator name.
8. README project structure tree — files in alphabetical position.
9. Test files in `mocktests/` and `realtests/` — alphabetical.
10. `requirements.txt` dependencies — alphabetical.

## 3. Indicator Function Signature Pattern

All `calculate_*` functions share this parameter order:

```python
def calculate_<indicator>(ticker: str, window: int,
                          interval: str = "1d",
                          count: int = 1
                          ) -> pd.Series:
```

Multi-param indicators (MACD, BB, STOCH, ADX) accept their specific
params before `interval`. The fetch pattern uses `_data_period` +
`_fetch_close` (or `_fetch_ohlcv` for multi-column data), followed by
`.dropna().iloc[-count:]` and an `IndexError` guard.

## 4. Indicator Registration Checklist

When adding a new indicator, ALL of these must be updated in
alphabetical position:

1. `indicators/<name>.py` — the implementation file.
2. `indicators/__init__.py` — the import re-export.
3. `main.py` — the import line, input prompt list, validation set,
   and `match/case` dispatch block.
4. `indicators/_data.py` — `_DEFAULT_WINDOWS` entry (if applicable).

## 5. Return Types

- Single-value indicators return `pd.Series`.
- Multi-value indicators (MACD, BB, STOCH, ADX) return tuples of
  `pd.Series`.
- The `_return_raw` parameter returns an additional raw data Series
  as a second tuple element.

## 6. Canonical Error Message

All data failures must surface as `IndexError` with this format:

```python
raise IndexError(
    f"Insufficient data for <INDICATOR>({window})"
    f" with count={count}"
)
```

## 7. TODO.md Entry Format

- Checkbox syntax: `- [ ]` pending, `- [x]` done.
- Tags: lowercase, single word, prefixed with `#` (e.g. `#indicator`,
  `#test`, `#docs`, `#cli`, `#infra`, `#bug`, `#refactor`).
- Owner tags: `@agent-name` format (e.g. `@feature-implementer`).
- New entries appended at the bottom of their section, never inserted
  at the top.

## 8. CHANGELOG Entry Rules

- Write from the user's perspective, one concise line each.
- Omit internal refactors, comment-only changes, and dependency bumps
  that do not change observable behaviour.
- Group changes under the correct section headers (`### Added`,
  `### Changed`, `### Fixed`, `### Security`).
- Only include section headers that have entries (omit empty ones).
- `### Security` entries state counts/classes only, never specifics.

## 9. Indicator Class Categories (Reasonableness Checks)

| Class | Indicators | Check Type |
|-------|-----------|------------|
| Moving-average | SMA, EMA, VWAP, AV, BB middle | `min <= result <= max` on raw data |
| Bounded oscillator | RSI, STOCH, ADX | `0 <= result <= 100` (or similar bound) |
| Stock-agnostic | MACD, RVOL | Finite values, no NaN |
| Raw-bounded volatility | ATR | `min(TR) <= result <= max(TR)` |
| Unbounded momentum | CCI, OBV, ROC | `pd.notna()` and `np.isfinite()` |

## 10. Smoothing Variant Rules

- Wilder RSI: `ewm(alpha=1/window, adjust=False)` — NOT SMA-based.
- EMA: `ewm(span=window, adjust=False)`.
- BB standard deviation: `ddof=0` (population) to match TradingView.
- ADX DI smoothing and ADX smoothing are separate parameters.

## 11. Release Gate Sequence

```
test-engineer (quality) → code-reviewer (architecture) →
security-auditor (trust) → consistency-guardian (conventions) →
release-manager (commit)
```

All gates must be green before the commit. Never skip or reorder.

## 12. Release Commit Format

```
Release X.Y.Z — <brief summary>
```

## 13. Semver Table

| Change Type | Bump | Example |
|-------------|------|---------|
| New indicator, new interval | MINOR | 1.7.0 → 1.8.0 |
| Test additions, refactoring | PATCH | 1.8.0 → 1.8.1 |
| Breaking CLI change | MAJOR | 1.x.x → 2.0.0 |
| Bug fix, doc improvement | PATCH | 1.8.0 → 1.8.1 |

## 14. README Structure

1. Title and description
2. Version badge
3. Features list
4. Syntax table (alphabetical by indicator name)
5. Error message table
6. Examples (alphabetical by indicator)
7. How It Works
8. Default Windows
9. Project Structure (alphabetical tree)
10. Tests
11. Agent-Based Development Workflow
12. License

## 15. Cross-Reference Rules

- Every doc that references agents must use the correct agent filename
  (e.g. `agents/feature-implementer.md`, not `agents/feature.md`).
- Every doc that references another doc must use relative links
  (e.g. `[changelog](update_changelog.md)`).

## 16. Backtester Conventions

- Entry/exit logic: all conditions must match (AND), fixed hold
  period, stop-loss checked during hold.
- Data cache: parquet files in `backtester/cache/`, one per ticker
  per interval.
- Batch download: use `yf.download(tickers, ...)` for batch fetching,
  not individual `yf.Ticker` calls.
- Condition syntax: `INDICATOR [params] [component] OP VALUE INTERVAL`
  — always ends with interval.
- Multi-component indicators require component: `BB upper >150 1d`,
  `STOCH 14,5,5 k>80 1d`, `MACD line>0 1d`.
- Simple indicators omit component: `RSI <30 1d`, `SMA 50 >200 1d`.
- Metrics use annualized return, Sharpe ratio, Sortino ratio, max
  drawdown, win rate, profit factor.
- Parquet cache format: columns are Date (index), Open, High, Low,
  Close, Volume; ticker and interval encoded in filename.
