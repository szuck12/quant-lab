# QuantLab Agents

This folder defines the **agent system** of the QuantLab project. Each
file is a persona: a detailed specification of a specialized role that
either a human contributor or an AI agent can embody to work on the
project.

The agents are the single source of truth for *who does what* in this
repository. The system model and the end-to-end task workflows live in:

- `docs/agents_overview.md` — the interaction model and assignment rules.
- `docs/agent_workflows.md` — step-by-step processes for every recurring
  task type, with the responsible agent named at each step.
- `AGENTS.md` (repository root) — the quick-reference usage guide for
  the whole system.

## How to Read a Persona

Every agent file uses the same template:

| Section | What it contains |
|---------|------------------|
| Role | One-paragraph mission statement |
| Scope | What the agent does — and does NOT do |
| Responsibilities | Numbered duty list |
| Constraints / Things NOT To Do | Imperative MUST NOT rules |
| Session Instructions | MEMORY.md read/append and verify.sh rules |
| Project-Specific Conventions | Agent-specific conventions (references `docs/conventions_reference.md`) |
| Tools / Commands | Commands the agent runs |
| Examples | Step-by-step workflow examples |
| Inputs / Outputs | What it receives, what it produces |
| Interactions | Table of with-whom / when / exchange |
| Standards Enforced | Links to the docs it enforces |
| Quick Reference | One-liner use-case and top rules |
| Handoff Checklist | Self-audit before handing work onward |

The **Session Instructions** and **Constraints** sections are written
as directives to the AI embodiment ("You MUST…"). Follow them exactly.

## The Roster

| File | Agent | Primary duty |
|------|-------|--------------|
| `task-orchestrator.md` | Task Orchestrator | Route, decompose, sequence, and verify all work |
| `idea-generator.md` | Idea Generator | Generate, collect, and triage ideas |
| `feature-implementer.md` | Feature Implementer | Write and refactor Python code |
| `indicator-specialist.md` | Indicator Specialist | Technical-indicator math and formulas |
| `data-engineer.md` | Data Engineer | yfinance data plumbing and period maps |
| `test-engineer.md` | Test Engineer | Author and run mock + real test suites |
| `code-reviewer.md` | Code Reviewer | Deep-dive architectural review |
| `consistency-guardian.md` | Consistency Guardian | Enforce conventions and structure |
| `documentation-expert.md` | Documentation Expert | README, docs, changelog wording |
| `security-auditor.md` | Security Auditor | Security review and dependency audits |
| `release-manager.md` | Release Manager | Versioning, changelog, release commits |

## How the Agents Are Used

A single task is rarely the work of one agent. The Task Orchestrator
assigns each task — and each part of a task — to the agent or group of
agents best specialized for it. The routing table in `AGENTS.md` and the
workflows in `docs/agent_workflows.md` describe these groupings.

In opencode, each persona is registered in `.opencode/opencode.json`,
bound to its file here, so the agents are directly invocable.