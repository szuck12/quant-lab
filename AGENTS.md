# AGENTS.md — QuantLab Agent System Guide

Entry point to QuantLab's agent-based development workflow. Read first;
full personas live in `agents/`.

## 1. What This Is

QuantLab uses a crew of specialized agents. The Task Orchestrator
assigns each task to the most specialized agent for it.

- **Canonical agent specs**: `agents/*.md`
- **Shared conventions**: `docs/conventions_reference.md`
- **End-to-end processes**: `docs/agent_workflows.md`
- **Interaction model**: `docs/agents_overview.md`
- **Persistent memory**: `MEMORY.md`

## 2. Quick Start

- **In opencode**: restart once after setup so `.opencode/opencode.json`
  loads. Delegate via the Task Orchestrator or name a specialist.
- **As a human**: open the persona file, follow its Workflow and
  Handoff Checklist, hand work to the next agent in the sequence.

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

## 4. Routing

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
| `MEMORY.md` | All agents (append decisions, corrections, lessons) |

## 6. Skills Index

Complex workflows are modularized into skill files that agents load on
demand. Each SKILL.md contains a step-by-step checklist and reference
to detail files.

| Skill | Trigger | Agent(s) |
|-------|---------|----------|
| `skills/add-indicator/` | Adding a new indicator | Orchestrator, Implementer, Test Engineer |
| `skills/release-cut/` | Cutting a release | Release Manager |
| `skills/security-audit/` | Running security scans | Security Auditor |

## 7. Handoff & Gate Rules

```
Idea Generator ──> Task Orchestrator ──> [specialist work] ──> Test Engineer
Test Engineer ──(failing work back)──> Feature Implementer
Consistency Guardian ──> Documentation Expert ──> Release Manager
Code Reviewer + Security Auditor ──(release gates)──> Release Manager
```

- **Test Engineer** is quality gate #1: nothing qualifies before the
  full mock suite is green.
- **Code Reviewer**, **Security Auditor**, and **Consistency
  Guardian** are release gates.
- **Release Manager** does not cut unless every gate is green.
- Failing work returns to the sender with reproduction, never leaks
  forward.

## 8. Task Lifecycle

```
Ideas (@idea-generator) → priority section → In Progress → Done → CHANGELOG
```

Every `TODO.md` entry may carry `@agent` owner tags per
`docs/maintain_todo.md`.

## 9. Escalation

- **Ambiguous spec** → ask the user (Task Orchestrator).
- **Very High / High security finding** → user immediately (Security
  Auditor).
- **"Ask" findings from a review** → user decision (Code Reviewer).

## 10. Pointers

- `agents/` — the canonical personas.
- `agents/README.md` — index and template explanation.
- `docs/conventions_reference.md` — shared conventions reference.
- `docs/agents_overview.md` — the interaction model.
- `docs/agent_workflows.md` — step-by-step processes.
- `MEMORY.md` — persistent decision and learning log.
