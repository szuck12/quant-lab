# Agent System Overview

This document describes the **model** behind QuantLab's agent system:
which agents exist, how they hand work to each other, and the rules that
govern assignment. For *how to use* each agent in practice, see
`AGENTS.md`. For *step-by-step processes*, see
`docs/agent_workflows.md`.

## 1. The Model

QuantLab is developed by a crew of eleven specialized agents coordinated
by a Task Orchestrator. The core idea: **a single task is rarely one
agent's job**. Every task, and every meaningful part of a task, is
assigned to the agent or group of agents most specialized for it.

- **Hub-and-spoke**: the Task Orchestrator is the hub. It receives all
  work, decomposes it, and dispatches to specialist agents.
- **Domain separation**: each agent owns a narrow slice (implementation,
  formulas, data, tests, reviews, conventions, docs, security,
  releases) so expertise is not diluted.
- **Gates, not vibes**: every handoff is verified. Some agents are
  *gates*: work cannot advance past them until they sign off.

## 2. The Roster

| Agent | Specialization | Role in the system |
|-------|----------------|--------------------|
| Task Orchestrator | Routing | Decomposes, assigns, sequences, verifies |
| Idea Generator | Research | Proposes and triages ideas |
| Feature Implementer | Code | Writes and refactors Python |
| Indicator Specialist | Math | Indicator formulas and reference values |
| Data Engineer | Data | yfinance plumbing and period maps |
| Test Engineer | Verification | Authors and runs the test suites |
| Code Reviewer | Architecture | Deep-dive review (§2–8) |
| Consistency Guardian | Conventions | Style, ordering, structure (§1) |
| Documentation Expert | Writing | README, docs, changelog wording |
| Security Auditor | Trust | Security and dependency review (§9) |
| Release Manager | Shipping | Versioning and release gate |

## 3. Assignment Rules

When any new task arrives, the Task Orchestrator assigns it using these
rules, in order:

1. **Specialization first.** Always choose the agent (or agents) most
   adept at the specific task or part of a task. Never assign specialist
   work to a generalist when a specialist exists.
2. **Decompose by expertise.** If a task spans domains (e.g. adding a
   new indicator involves formula research, code, data, tests, and
   docs), split it into parts and assign each part to its expert.
3. **One lead.** Each task has a single lead agent accountable for the
   outcome; supporting agents collaborate around it.
4. **Acceptance criteria.** Every assignment carries explicit acceptance
   criteria so the receiving agent can self-verify.
5. **Parallelize safely.** Independent parts (e.g. implementation and
   data-layer work) run in parallel. Dependent parts run in sequence.
6. **Gates are invariant.** Quality, architecture, security, and
   conventions gates cannot be bypassed, reordered, or skipped.

> Example: "Add a new indicator" is not assigned to one agent. The
> Indicator Specialist produces the formula spec, the Feature
> Implementer and Data Engineer build it, the Test Engineer proves it,
> the Consistency Guardian checks conventions, the Documentation Expert
> writes the docs, and the Release Manager ships it — sequenced and
> verified by the Task Orchestrator.

## 4. Authority and File Ownership

Each agent owns the files and processes in its specialization. See the
File Ownership table in `AGENTS.md` §5. Ownership means: the agent is
the authority on that surface and is expected to keep it correct.

## 5. Handoff Model

### 5.1 The happy path

```
Idea Generator ──> Task Orchestrator ──> [specialists] ──> Test Engineer
      ──> Consistency Guardian ──> Documentation Expert
      ──> [Code Reviewer + Security Auditor gates] ──> Release Manager
```

### 5.2 The rework loop

When a handoff fails its acceptance criteria, it returns to the sender
with a reproduction or a reason — it never leaks forward:

```
Feature Implementer ──> Test Engineer ──(red)──> Feature Implementer
Security Auditor ──> Feature Implementer ──(fix)──> Security Auditor
```

### 5.3 Escalation paths

- **Ambiguous spec** → the Task Orchestrator asks the user.
- **Very High / High security finding** → the Security Auditor escalates
  to the user immediately.
- **"Ask" findings** → the Code Reviewer routes them to the user as
  decisions.

## 6. How Agents Find Assignments

- **TODO.md**: entries carry `@agent` owner tags, so the responsible
  agent(s) are visible at a glance (e.g.
  `@feature-implementer @test-engineer`). See `docs/maintain_todo.md`.
- **Interesting, urgent, or cross-cutting work**: the Task Orchestrator
  intercepts it at intake and decomposes it before any agent acts.

## 7. Relationship to Existing Documentation

| Doc | Role | Agent relationship |
|-----|------|--------------------|
| `docs/agent_workflows.md` | Step-by-step processes | Names the agent for each step |
| `docs/adding_indicator.md` | Indicator how-to | Annotated with the agent per step |
| `docs/maintain_todo.md` | TODO lifecycle | Defines the `@agent` tag convention |
| `docs/update_changelog.md` | Versioning process | Run by the Release Manager |
| `docs/code_review_guide.md` | Review checklists | §1 Consistency, §2–8 Reviewer, §9 Security |
| `docs/formulas.md` | Indicator formulas | Owned by the Indicator Specialist |
| `docs/commenting_guidelines.md` | Code conventions | Enforced by the Consistency Guardian |
| `SECURITY.md` | Security policy | Audited by the Security Auditor |