# Agent Workflows

This document describes the step-by-step processes of QuantLab's agent
system: **which agent does which task, and how they interact and work
together**. Every recurring task type has a flow below with the
responsible agent named at each step. The Task Orchestrator routes work
through these flows; each agent's persona in `agents/` adds detail.

Rules that apply to every workflow:

- The **Test Engineer** is quality gate #1: nothing qualifies before the
  full mock suite is green.
- The **Code Reviewer** and **Security Auditor** are release gates.
- The **Consistency Guardian** audits conventions before docs/release.
- Work that fails a handoff returns to the sender with reproduction.
- Every assignment is recorded as `@agent` tags in `TODO.md`.

---

## Workflow A — Add a New Indicator (the flagship task)

Maps one-to-one onto `docs/adding_indicator.md`. A new indicator is a
MINOR release.

| Step | Owner | Output |
|------|-------|--------|
| 0 | Idea Generator / Task Orchestrator | Idea triaged; TODO entry created (Documentation Expert) |
| 1 | Indicator Specialist | Spec: formula variant, default window, data needs, edge cases, reference values |
| 2a–2f | Feature Implementer (+ Data Engineer) | `indicators/<name>.py`, registration in `__init__.py` + `main.py`, `_DEFAULT_WINDOWS` entry |
| 2a/2d | Data Engineer | Period-map / data-helper changes, fixture columns |
| 3a–3b | Test Engineer | Mock tests (≥14 data sizes) + dispatch tests |
| 4a–4c | Test Engineer (+ Indicator Specialist) | Real tests + reasonableness checks |
| 5 | Test Engineer | Full suite green (mock + real) — quality gate #1 |
| — | Consistency Guardian | Conventions, alphabetical order, tree audit |
| 6 / 6c | Documentation Expert (+ Indicator Specialist) | README tables/examples; `docs/formulas.md` section |
| 7 | Release Manager | MINOR bump; CHANGELOG; release commit |
| — | Code Reviewer + Security Auditor | Pre-release gates before the commit |

Handoff chain:

```
indicator-specialist → feature-implementer ⇄ data-engineer → test-engineer
  → consistency-guardian → documentation-expert → code-reviewer
  + security-auditor → release-manager
```

---

## Workflow B — Fix a Bug

A bug fix is a PATCH release. The Test Engineer reproduces before any
fix is written.

| Step | Owner | Output |
|------|-------|--------|
| 1 | Test Engineer | Failing test mirroring the report; reproduction |
| 2 | Feature Implementer | Code fix (implementation only) |
| 3 | Test Engineer | Full mock suite; new test goes green — quality gate #1 |
| 4 | Consistency Guardian | Conventions audit of the diff |
| 5 | Documentation Expert | CHANGELOG wording (Fixed), README if user-visible |
| 6 | Release Manager | PATCH bump; release commit |

Failing step 3 returns to step 2 with reproduction.

---

## Workflow C — Dependency Bump / Security Fix

A dependency change is verified by the Security Auditor before and
after. Security releases are PATCH with counts/classes-only entries.

| Step | Owner | Output |
|------|-------|--------|
| 1 | Security Auditor | `pip-audit` + Dependabot review; severity grading |
| 2 | Feature Implementer | Pin update in `requirements.txt` |
| 3 | Test Engineer | Full mock + real suites |
| 4 | Security Auditor | Re-scan; re-verify the fix |
| 5 | Release Manager | PATCH bump; `### Security` entry (counts/classes only) |

---

## Workflow D — Refactor

A behavior-preserving refactor is a PATCH release. The Test Engineer
proves no behavior change.

| Step | Owner | Output |
|------|-------|--------|
| 1 | Feature Implementer + Consistency Guardian | Restructure / stylize per conventions |
| 2 | Test Engineer | Full suite still green — no behavior change |
| 3 | Code Reviewer | §8 structural audit; Take/Ask table |
| 4 | Release Manager | PATCH bump; release commit |

---

## Workflow E — Docs-Only Change

| Step | Owner | Output |
|------|-------|--------|
| 1 | Documentation Expert (+ Indicator Specialist for formulas) | Updated docs, tree, changelog wording |
| 2 | Consistency Guardian | Tree alphabetical + complete; cross-refs resolve |
| 3 | Release Manager | PATCH bump (doc improvements); release commit |

---

## Workflow F — Idea Intake

| Step | Owner | Output |
|------|-------|--------|
| 1 | Idea Generator | Idea brief (problem, solution, sketch, priority) |
| 2 | Idea Generator | `TODO.md` Ideas entry tagged `@idea-generator` |
| 3 | Task Orchestrator | Triage + promotion to a priority section |
| 4 | Documentation Expert | Wording of the priority TODO entry |
| 5 | Task Orchestrator | Route into Workflow A/B/C/D as appropriate |

---

## Workflow G — Release (all work done)

The Release Manager only cuts after every gate is green.

| Step | Owner | Output |
|------|-------|--------|
| 1 | Test Engineer | Full mock suite green |
| 2 | Code Reviewer | Pre-release audit (§2–8) with Take/Ask table |
| 3 | Security Auditor | §9 scan clean; findings handled |
| 4 | Consistency Guardian | Conventions + tree + formatting green |
| 5 | Documentation Expert | Badge + changelog wording synchronized |
| 6 | Release Manager | `Release X.Y.Z — <summary>` commit; TODO → Done |

---

## Workflow H — Run or Modify the Backtester

| Step | Owner | Output |
|------|-------|--------|
| 1 | Backtest Engineer | Understands the requested backtester change or bug fix |
| 2 | Backtest Engineer | Implements changes to `backtester/` package |
| 3 | Backtest Engineer | Runs `ruff check backtester/` and `python3 run_mock_tests.py` |
| 4 | Test Engineer | Verifies with mock suite (521+ tests) |
| 5 | Indicator Specialist | Validates batch indicator formulas if changed |
| 6 | Consistency Guardian | Checks conventions and code style |
| 7 | Documentation Expert | Updates CLI docs and examples if user-facing |
| 8 | Release Manager | Releases as MINOR or MAJOR bump depending on scope |

### Backtester-Specific Notes

- Entry/exit logic: all conditions must match (AND), fixed hold period.
- Data cache: parquet files in `backtester/cache/`.
- Batch download: `yf.download()` for multi-ticker fetching.
- Condition syntax: `INDICATOR [params] [component] OP VALUE INTERVAL`.
- Metrics: Sharpe, Sortino, max drawdown, win rate, profit factor.

---

## Interaction Graph

```
                    ┌────────────────────────────────────┐
                    │         Task Orchestrator          │
                    └──────┬──────┬──────┬──────┬────────┘
                           │      │      │      │
        ┌──────────────────┤      │      │      ├───────────────────┐
        ▼                  ▼      ▼      ▼      ▼                    ▼
   idea-generator    feature-  data-  test-  indicator-       documentation-
   (proposes)        implement- engine engineer specialist     expert (writes)
                     er (codes)
                                          │
                    ┌─────────────────────┤
                    ▼                     ▼
        consistency-guardian      code-reviewer + security-auditor
        (conventions audit)              (release gates)
                    │                     │
                    └──────────┬──────────┘
                               ▼
                      release-manager (ships)
```

---

## Verification Commands by Step

| Step | Command |
|------|---------|
| Quality gate #1 (mock) | `python3 run_mock_tests.py` |
| Real suite | `python3 run_real_tests.py` |
| Feature Implementer pre-handoff | `ruff check .` ; `python3 main.py` smoke test |
| Security scans | Commands in `docs/code_review_guide.md` §9c |
| Consistency checks | `ruff check` / `mypy` when configured |
| Release commit message | `Release X.Y.Z — <brief summary>` |