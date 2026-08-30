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

## Corrections & Lessons Learned

<!-- Record mistakes and what was learned from them. -->

- **File naming**: `documentation-expect.md` was a typo for
  `documentation-expert.md`. Always verify agent filenames before
  committing.
- **JSON permissions**: opencode.json agent permission objects must use
  the last-match-wins pattern (`"*": "ask"` first, specific allows
  last) to avoid global allow overriding specific deny.

## Last Session State

<!-- Brief snapshot of where work left off. Updated at end of session. -->

- Current version: 1.8.1
- All 422 mock tests passing.
- All agent files have Session Instructions (MEMORY.md + verify.sh)
  and Quick Reference sections.
- Shared conventions live in `docs/conventions_reference.md`.
- Skill files created: `skills/add-indicator/`, `skills/release-cut/`,
  `skills/security-audit/`.
- Backtester agent added: `agents/backtest-engineer.md`.
- Backtester package created: `backtester/` (cli, data_pipeline,
  batch_indicators, engine, metrics, reporting).
- BACKTEST command integrated into `main.py` dispatch.
