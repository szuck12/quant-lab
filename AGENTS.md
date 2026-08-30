# AGENTS.md — QuantLab Agent System Guide

This is the entry point to QuantLab's agent-based development workflow.
It tells you which agent does what, how to use them, and how they hand
work to each other. Read this file first; the full persona for each
agent lives in `agents/`.

## 1. What This Is

QuantLab is developed through a crew of specialized agents. A single
task is rarely one agent's job — the Task Orchestrator assigns each task
(and each part of a task) to the agent or group of agents best equipped
for it.

- **Canonical agent specs**: `agents/*.md`
- **End-to-end processes**: `docs/agent_workflows.md`
- **Interaction model**: `docs/agents_overview.md`

## 2. Quick Start

- **In opencode**: restart the app once after setup so the agent
  registration in `.opencode/opencode.json` loads. Then delegate with
  the Task Orchestrator (e.g. "have the orchestrator add a new
  indicator") or name a specialist directly ("have the test engineer
  review this change").
- **As a human**: open the persona for the job, follow its Workflow and
  Handoff Checklist, and hand work to the next agent named in
  `docs/agent_workflows.md`.

## 3. The Roster

| Agent | Role | Assign when... | Gate when... |
|-------|------|----------------|--------------|
| Task Orchestrator | Routes and decomposes all work | Starting any multi-step task | Every handoff |
| Idea Generator | Idea generation and triage | Brainstorming, new features | An idea is ready to schedule |
| Feature Implementer | Writes and refactors code | Implementation is needed | Code must be verified |
| Indicator Specialist | Indicator math and formulas | Adding/changing indicators | Formula correctness |
| Data Engineer | yfinance data plumbing | Data layer, periods, intervals | Data robustness |
| Test Engineer | Authors and runs tests | Code needs verification | Quality gate #1 |
| Code Reviewer | Architectural review | Significant change, release | Architecture gate |
| Consistency Guardian | Conventions and structure | Style/ordering checks | Conventions gate |
| Documentation Expert | README, docs, changelog wording | Anything user-visible changes | Doc accuracy |
| Security Auditor | Security and dependency auditing | Release, dependency change | Security gate |
| Release Manager | Versioning and release | All work is done | Final release gate |

## 4. Routing — "You want to… | Use"

| You want to… | Use |
|--------------|-----|
| Brainstorm / triage a feature | Idea Generator (+ Documentation Expert for the TODO entry) |
| Add an indicator | Indicator Specialist → Feature Implementer → Data Engineer → Test Engineer → Documentation Expert |
| Fix a bug | Test Engineer (reproduce) → Feature Implementer → Test Engineer (verify) |
| Bump a dependency | Security Auditor → Feature Implementer → Test Engineer → Security Auditor |
| Refactor | Feature Implementer + Consistency Guardian → Test Engineer → Code Reviewer |
| Write / update docs | Documentation Expert (+ Consistency Guardian) |
| Answer a design question | Code Reviewer (§8) |
| Audit security | Security Auditor (§9) |
| Release | Release Manager (+ Code Reviewer, Security Auditor gates) |
| Check conventions | Consistency Guardian (§1) |

## 5. File Ownership

| Files | Owning agent |
|-------|--------------|
| `main.py`, `indicators/**`, `requirements.txt`, `pytest.ini` | Feature Implementer |
| `indicators/_data.py`, `mocktests/conftest.py` | Data Engineer |
| `mocktests/**`, `realtests/**`, `run_*_tests.py` | Test Engineer |
| `README.md`, `docs/**` | Documentation Expert |
| `docs/formulas.md` | Indicator Specialist |
| `SECURITY.md`, dependency pins | Security Auditor |
| `CHANGELOG.md`, version numbers | Release Manager |
| `TODO.md` entries | Idea Generator (Ideas), Task Orchestrator (task tags) |

## 6. Invocation

- **In opencode**: agents are defined in `agents/*.md` and registered in
  `.opencode/opencode.json`, each bound to its persona. Trigger them via
  the agent picker or by Task delegation from the Task Orchestrator.
- **Manually**: read the persona file, follow its Operating
  Instructions, produce its outputs, then complete its Handoff
  Checklist before passing work to the next agent.

## 7. Handoff & Gate Rules

```
Idea Generator ──> Task Orchestrator ──> [specialist work] ──> Test Engineer
Test Engineer ──(failing work back)──> Feature Implementer
Consistency Guardian ──> Documentation Expert ──> Release Manager
Code Reviewer + Security Auditor ──(release gates)──> Release Manager
```

- The **Test Engineer** is quality gate #1: nothing qualifies before the
  full mock suite is green.
- The **Code Reviewer**, **Security Auditor**, and **Consistency
  Guardian** are release gates that run before a release.
- The **Release Manager** does not cut unless every gate is green.
- Failing work returns to the sender with reproduction, never leaks
  forward.

## 8. Task Lifecycle (equals the TODO.md lifecycle)

```
Ideas (@idea-generator) → priority section → In Progress → Done → CHANGELOG
```

Every `TODO.md` entry may carry `@agent` owner tags so the responsible
agent is visible at a glance (e.g. `@feature-implementer @test-engineer`).
See `docs/maintain_todo.md` for the entry rules.

## 9. Per-Agent Usage

### Task Orchestrator
Use when starting any task. It decomposes, assigns, sequences, and
verifies. Top rules: assign to the most specialized agent; put
acceptance criteria in every brief; never skip the gates; ask the user
when a brief is ambiguous.

### Idea Generator
Use when brainstorming or triaging. It writes schedulable proposals with
acceptance criteria and maintains the `TODO.md` Ideas section. Top
rules: propose only; tag entries `@idea-generator`; research
authoritative defaults before proposing indicators.

### Feature Implementer
Use for any Python change. Top rules: implement only the brief; keep
signatures and every alphabetical order intact; run `ruff check` and a
`python3 main.py` smoke test before handoff; never fix tests yourself.

### Indicator Specialist
Use for any indicator formula. Top rules: ground formulas in
authoritative references; state the smoothing variant; provide
reference values as executable assertions; keep `docs/formulas.md`
current; flag divergent conventions to the user.

### Data Engineer
Use for data layer, period maps, intervals, fixtures. Top rules: verify
thresholds against yfinance availability; surface failures as
`IndexError`; keep `test_data_period.py` in sync; preserve
`_data` helper names and signatures.

### Test Engineer
Use to verify any code change. Top rules: write a failing test first
when fixing a bug; mock tests stay deterministic, real tests stay
mathematically sound; run the full suite, never a single file; certify
handoffs or return them with reproduction.

### Code Reviewer
Use for architectural depth. Top rules: audit, never fix; findings cite
`file:line`; do not duplicate the Consistency Guardian ( §1 ) or
Security Auditor ( §9 ); deliver the Take/Ask action table.

### Consistency Guardian
Use for style, ordering, structure. Top rules: prefer machine checks;
report violations with `file:line`, blocking vs suggestion; never edit
files; verify the README project tree is alphabetical and complete.

### Documentation Expert
Use for any user-visible change. Top rules: never invent behaviour;
keep the badge equal to the latest changelog entry; insert tree and
doc entries in alphabetical position; spot-check example commands.

### Security Auditor
Use before releases and on dependency changes. Top rules: run the §9
scans; grade by reachability; escalate High/Very High immediately; keep
specific vulnerability details out of committed artifacts; re-verify
fixes.

### Release Manager
Use to ship. Top rules: never cut while a gate is red or unrun (tests →
review → security → consistency → commit); pick the bump from the semver
table; write `### Security` entries as counts/classes only; commit with
`Release X.Y.Z — <summary>`.

## 10. Escalation

- **Ambiguous spec** → ask the user (Task Orchestrator).
- **Very High / High security finding** → user immediately (Security
  Auditor).
- **"Ask" findings from a review** → user decision (Code Reviewer).

## 11. Pointers

- `agents/` — the canonical personas.
- `agents/README.md` — index and template explanation.
- `docs/agents_overview.md` — the interaction model and assignment rules.
- `docs/agent_workflows.md` — step-by-step processes with per-step owners.
- Existing docs each agent enforces are linked from its persona file.