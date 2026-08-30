---
name: security-audit
description: Workflow for running security scans in QuantLab. Loaded by the Security Auditor before releases and on dependency changes.
---

# Security Audit — Security Auditor Workflow

## Overview

This skill runs the full §9c security scan checklist. Loaded by the
Security Auditor before releases and on dependency changes.

## Checklist

- [ ] Step 1: Secrets scan
- [ ] Step 2: Dangerous primitives scan
- [ ] Step 3: ANSI injection probe
- [ ] Step 4: Dependency audit
- [ ] Step 5: Repository hygiene
- [ ] Step 6: Grade findings by reachability
- [ ] Step 7: Escalate Very High/High findings
- [ ] Step 8: Hand fixes to implementer
- [ ] Step 9: Re-verify fixes
- [ ] Step 10: Sign off

## Scan Commands

### Step 1 — Secrets Scan

```bash
git log --all -p | grep -inE \
  '(ghp_|gho_|github_pat_|AKIA[A-Z0-9]{16}|BEGIN [A-Z ]*PRIVATE KEY)'
git ls-files | grep -iE '\.env|secret|token|credential|\.pem'
```

### Step 2 — Dangerous Primitives

```bash
grep -rnE 'eval\(|exec\(|compile\(|__import__|pickle|yaml\.load|subprocess|os\.system|shell\s*=\s*True' --include='*.py' .
```

### Step 3 — ANSI Injection Probe

```bash
printf 'AA\x1b[31mPL\x1b[0m SMA' | python3 main.py | cat -v
```

### Step 4 — Dependency Audit

```bash
pip install pip-audit
pip-audit
```

Verify exact `==` pins in `requirements.txt`.

### Step 5 — Repository Hygiene

```bash
git ls-files | grep -iE '\.DS_Store|cache|\.env|\.log$'
git status --porcelain --untracked-files=all
cat .gitignore
```

## Severity Scale

Per `docs/conventions_reference.md`:

| Severity | Definition | Response |
|----------|-----------|----------|
| Very High | Live secret or exploitable path | Revoke/rotate FIRST; PATCH same day |
| High | Realistic exploit with modest preconditions | Fix within days |
| Medium | Weakens posture; exploitable after future change | Next release |
| Low | Hygiene; no realistic path today | Batch into TODO.md |

## Reporting Protocol

- Never open a public issue with a live secret.
- Use GitHub private security advisory for external reports.
- Rotate/revoke before scrubbing history.
- Counts/classes only in committed artifacts.
- Detailed log kept outside the repository.

## Fix Workflow

1. Hand finding to `feature-implementer` via Task Orchestrator.
2. After fix, re-run the relevant scan command.
3. Verify finding is resolved.
4. Sign off for the release gate.

## Sign-Off

All §9c scans complete, findings graded, escalations sent, fixes
re-verified. Ready for release gate.
