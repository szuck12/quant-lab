---
name: add-indicator
description: End-to-end workflow for adding a new technical indicator to QuantLab. Load this skill when the task is to add, create, or implement a new indicator.
---

# Add New Indicator — Orchestrator Workflow

## Overview

This skill coordinates adding a new indicator through all agent gates.
The orchestrator loads this checklist; specialists load their detail
files (`implement.md`, `test-mock.md`, `test-real.md`).

## Checklist

- [ ] Step 1: Idea Generator creates TODO entry
- [ ] Step 2: Indicator Specialist produces formula spec
- [ ] Step 3: Feature Implementer implements + registers
- [ ] Step 4: Data Engineer adjusts period maps if needed
- [ ] Step 5: Test Engineer writes mock tests
- [ ] Step 6: Test Engineer writes real tests
- [ ] Step 7: Test Engineer runs full suite — quality gate #1
- [ ] Step 8: Consistency Guardian audits conventions
- [ ] Step 9: Documentation Expert updates README + docs
- [ ] Step 10: Code Reviewer runs deep-dive audit
- [ ] Step 11: Security Auditor runs security scan
- [ ] Step 12: Release Manager cuts MINOR release

## Per-Step Details

### Step 1 — Idea Generator
Create a TODO entry tagged `@idea-generator` in the Ideas section.
Format: `- [ ] Add <INDICATOR> indicator (#indicator) @idea-generator`.
Brief must include: Problem, Proposed Solution, Design Sketch, Priority,
Acceptance Criteria.

### Step 2 — Indicator Specialist
Deliverable: full spec per `docs/adding_indicator.md` section 1.
Contents: name, canonical formula, default window, data requirements,
edge cases, reference values as `pytest.approx` assertions.
Owns `docs/formulas.md`.

### Step 3 — Feature Implementer
Load `skills/add-indicator/implement.md` for code patterns.
Deliverable: implemented `indicators/<name>.py`, registered in all 4
locations per conventions_reference.md §4, `ruff check` clean.

### Step 4 — Data Engineer
Only if the indicator needs new columns, intervals, or custom data
handling. Adjust `_DATA_PERIOD_MAP`, `_DEFAULT_WINDOWS`, and
`conftest.py` fixtures if needed.

### Step 5 — Test Engineer (Mock)
Load `skills/add-indicator/test-mock.md` for the test template.
Deliverable: `mocktests/test_calculate_<indicator>.py` with 14+
categories per conventions_reference.md §9.

### Step 6 — Test Engineer (Real)
Load `skills/add-indicator/test-real.md` for the test template.
Deliverable: `realtests/test_calculate_<indicator>.py` with 3+
tickers, 3+ windows, weekly interval, window=1, dispatch test.

### Step 7 — Quality Gate #1
Run `bash scripts/verify.sh`. Full mock suite must be green.
If red, return to Feature Implementer with reproduction.

### Step 8 — Consistency Guardian
Audit: alphabetical ordering in all 4 registration points, README
tree includes new file, `docs/formulas.md` has new section, no
obvious-obvious comments, docstrings follow conventions_reference.md §1.

### Step 9 — Documentation Expert
Update: README syntax table (alphabetical), example command, project
tree, `docs/formulas.md` cross-ref, changelog entry wording.

### Step 10 — Code Reviewer
Deep-dive per `docs/code_review_guide.md` sections 2–8.
Verify: function follows pattern, mock coverage complete, error
handling correct, docs match code.

### Step 11 — Security Auditor
Pre-release scan per `docs/code_review_guide.md` section 9.
Run the 5 §9c scan commands. Grade by reachability.

### Step 12 — Release Manager
Bump: new indicator → MINOR. Commit: `Release X.Y.Z — Add <INDICATOR>
indicator`. Sync README badge.

## Verification

After the final release commit, run `bash scripts/verify.sh --full`
to confirm everything is green.
