---
name: release-cut
description: Workflow for cutting a release in QuantLab. Loaded by the Release Manager when all work is done and gates are green.
---

# Release Cut — Release Manager Workflow

## Overview

This skill coordinates the release process through all gates.
Loaded by the Release Manager when all implementation work is complete.

## Checklist

- [ ] Step 1: Confirm all gates have run and are green
- [ ] Step 2: Determine the version bump from semver table
- [ ] Step 3: Structure CHANGELOG entry
- [ ] Step 4: Sync README badge
- [ ] Step 5: Move TODO items to Done
- [ ] Step 6: Commit with release message
- [ ] Step 7: Notify the user

## Per-Step Details

### Step 1 — Gate Verification

Confirm each gate has run:

| Gate | Agent | Command |
|------|-------|---------|
| Quality | test-engineer | `bash scripts/verify.sh` |
| Architecture | code-reviewer | §2–§8 audit complete |
| Security | security-auditor | §9 scan complete |
| Consistency | consistency-guardian | §1 audit complete |

If any gate is red or unrun, STOP. Do not proceed.

### Step 2 — Version Bump

Use the semver table per `docs/conventions_reference.md` §13:

| Change Type | Bump |
|-------------|------|
| New indicator, new interval | MINOR |
| Test additions, refactoring | PATCH |
| Breaking CLI change | MAJOR |
| Bug fix, doc improvement | PATCH |

### Step 3 — CHANGELOG Entry

Per `docs/conventions_reference.md` §8:
- Single concise line from user's perspective.
- Group under `### Added`, `### Changed`, `### Fixed`, or
  `### Security`.
- Only include sections that have entries.
- `### Security` = counts/classes only.

### Step 4 — README Badge

Sync the version badge to the new version:

```markdown
Current version: **X.Y.Z** — [Changelog](CHANGELOG.md)
```

### Step 5 — TODO.md Updates

Move completed items from **In Progress** to **Done**.
Mark checkboxes as `- [x]`.

### Step 6 — Release Commit

Commit message must match exactly:

```
Release X.Y.Z — <brief summary>
```

Examples:
- `Release 1.8.0 — Add agent-based development workflow`
- `Release 1.8.1 — Fix MACD histogram calculation`

### Step 7 — Notify

Report the release to the user with a summary of what changed.

## Verification

After the commit, run `bash scripts/verify.sh` one final time to
confirm the released code is clean.
