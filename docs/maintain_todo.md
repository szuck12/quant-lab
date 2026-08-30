# Maintaining TODO.md

This document describes how to keep `TODO.md` up to date and explains how it
relates to the other project documentation.

## Purpose

`TODO.md` tracks **planned** and **in-progress** work — features that haven't
shipped yet, bugs not yet fixed, ideas still being evaluated. It looks forward.

For **historical** records of what has already shipped, see `CHANGELOG.md`.

## Sections and Their Lifecycles

| Section | Purpose | Lifecycle |
|---------|---------|-----------|
| **In Progress** | What's actively being worked on. | At most 1–2 items. When an item ships, move it to **Done** and record the release in `CHANGELOG.md`. |
| **Done** | Recently completed items. | Prune periodically — once an item is recorded in a release, it can be removed. |
| **High Priority** | Important changes that should be done soon. | Items arrive here when a clear need is identified (bug, requested feature, etc.). |
| **Medium Priority** | Should get done, not urgent. | Items may be promoted or demoted as priorities shift. |
| **Low Priority** | Nice-to-haves. | Items that are worth doing but have no urgency. |
| **Ideas** | Interesting ideas not yet committed to implementation. | When an idea solidifies into a concrete plan, move it to one of the priority sections. If it's rejected or becomes irrelevant, remove it. |

### Item Flow

```
Ideas → Priority (High/Medium/Low) → In Progress → Done → pruned
```

Items can skip the Ideas stage (e.g. a bug report goes straight to a priority
section). Items can be demoted or removed at any point.

## When to Update

- **A change is requested or a bug is found.** Add an unchecked item (`[ ]`)
  to the appropriate priority section based on importance.
- **An idea comes up.** Add it to **Ideas** with an unchecked box.
- **Work begins.** Move the item to **In Progress**.
- **Work ships.** Move the item to **Done**, check the box (`[x]`), and record
  the change in `CHANGELOG.md` following the [changelog process](update_changelog.md).
- **An item is no longer relevant.** Remove it (no need to leave zombie entries).

## Relationship to Other Documentation

| File | Role | How It Differs from TODO.md |
|------|------|-----------------------------|
| `CHANGELOG.md` | Records what shipped in each release. | Backward-looking. A TODO item moves here once completed. |
| `adding_indicator.md` | Step-by-step guide for implementing a new indicator. | How-to for the *implementation*. TODO.md tracks *what* is planned; `adding_indicator.md` explains *how* to build it. |
| `update_changelog.md` | Process for version bumps and changelog entries. | Works in tandem: when an item ships, move it in TODO.md *and* record it in CHANGELOG.md. |
| `agents_overview.md` | The agent system's interaction model and assignment rules. | Names the actors; TODO.md `@agent` tags record their assignments per task. |
| `agent_workflows.md` | Step-by-step processes with the responsible agent per step. | TODO.md tracks *what*, the workflows track *who/when*. |

## Entry Conventions

Every entry is a Markdown checkbox list item:

```
- [ ] Brief action-oriented description (#tag)
```

### Agent Owner Tags

Every entry may carry `@agent` owner tags so the responsible agent(s)
are visible at a glance. Use `@`-prefixed agent names from the roster in
`AGENTS.md` (e.g. `@feature-implementer`, `@test-engineer`,
`@security-auditor`, `@release-manager`, `@idea-generator`). Ideas
section entries are always tagged `@idea-generator`; priority and
In Progress entries carry the tags of the agents assigned to execute
them, set by the Task Orchestrator.

```
- [ ] Implement the new interval (#indicator,
      @indicator-specialist @feature-implementer @test-engineer)
```

Price tags are lowercase, single word, prefixed with `#`. Use any tag that fits;
common ones:

| Tag | When to Use |
|-----|-------------|
| `#indicator` | Adding or modifying a technical indicator |
| `#test` | Test changes (new tests, fixing tests) |
| `#bug` | Bug fixes |
| `#docs` | Documentation changes |
| `#refactor` | Code restructuring without behaviour change |
| `#cli` | Command-line interface changes |
| `#infra` | Build, CI, project config |

For completed items, check the box and prefix with the completion date
(`YYYY-MM-DD`):

```
- [x] 2026-05-25 — Fix realtest conftest 1s delay applying to mock tests
      (#test, #bug)
```

### Done Section Pruning

When the **Done** section has **10 or more** items, prune it to at most
**9** items by removing the oldest entries.  This keeps the section
focused on recently completed work without accumulating historical noise.

Never remove items from **In Progress**, **High Priority**,
**Medium Priority**, **Low Priority**, or **Ideas** sections — only
the Done section is pruned.

Keep descriptions concise but clear enough that someone reading the TODO
understands what the task involves without needing additional context.

### Entry Ordering

New entries are appended at the **bottom** of their section (after any
existing entries), not inserted at the top. This preserves a rough
chronological order within each priority group and avoids merge
conflicts when multiple people add entries in the same session.
