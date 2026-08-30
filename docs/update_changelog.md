# Updating the Changelog

This document describes the process to follow whenever a change is made to
the project. It governs version numbering, changelog entries, and README
updates.

## Agents Involved

The **Release Manager** leads this process: it decides the semver bump,
structures the changelog, and creates the release commit. Supporting
agents:

- **Documentation Expert** — drafts changelog entry wording and keeps
  the README version badge synchronized (Step 3).
- **Security Auditor** — supplies the `### Security` entry content on
  security releases (counts/classes only, Step 2).
- **Code Reviewer** — runs the pre-release audit that a release
  candidate must pass before Step 4.
- **Test Engineer** — provides the full-suite green verdict that gates
  the release.

See `agents/release-manager.md` and `docs/agent_workflows.md`
(Workflow G) for the full release procedure.

## Step 1 — Determine the New Version

Follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):

| Bump | Rule | Example |
|------|------|---------|
| MAJOR | Backward-incompatible changes (breaking CLI syntax, removing features) | 1.0.0 → 2.0.0 |
| MINOR | New backward-compatible functionality (new indicator, new interval) | 1.0.0 → 1.1.0 |
| PATCH | Bug fixes, test additions, doc improvements, refactoring | 1.0.0 → 1.0.1 |

When a component is bumped, all components to its right reset to zero
(e.g. 1.2.3 → 2.0.0, 1.2.3 → 1.3.0).

## Step 2 — Update CHANGELOG.md

Add a new section at the top of `CHANGELOG.md` (before the `## [Unreleased]`
entry if present, or before the most recent release otherwise):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security
```

Include only the section headers that have entries. Omit empty sections.

`### Security` entries follow a special rule once the repository is
public: state only the number and general nature of what was fixed
(e.g. "Fixed 2 known security vulnerabilities in pinned dependencies").
Never name specific packages, versions, or CVE identifiers in committed
changelog entries; those details belong in the maintainer's private
security log and GitHub security advisories (see `code_review_guide.md`,
Section 9b). The **Security Auditor** agent supplies this entry's
content.

### What to include

- ✅ **User-facing changes** — new CLI behaviour, indicators, error messages,
    interval support.
- ✅ **Test infrastructure changes** — new test suites, runners, fixtures
    that affect how developers validate the project.
- ✅ **Documentation changes** that affect how users interact with the
    project (README, adding_indicator, changelog process).
- ❌ **Internal refactoring** — renamed variables, reformatted code, moved
    files without changing behaviour.
- ❌ **Comment or whitespace-only changes** — linting fixes, docstring
    rewording that doesn't change meaning.
- ❌ **Dependency bumps** that don't change observable behaviour.

Each entry should be a single concise line describing the change from the
user's perspective.

### Grouping

Group related changes under a single version. Most releases should contain
multiple changes rather than one per version.

## Step 3 — Update README.md

1. **Version badge** — update the version in the badge line under the title:
   `Current version: **X.Y.Z**`

   The README only ever shows the current (latest) release version. Full
   version history lives exclusively in CHANGELOG.md — do not add a
   version list or past releases to the README.

2. **Project structure** — if files were added or removed, update the
   directory tree to match.

3. **Feature documentation** — if the CLI syntax, indicator list, or usage
   examples changed, update the relevant sections.

## Step 4 — Commit

Create a single commit with the message format:

```
Release X.Y.Z — <brief summary>
```

Example:

```
Release 1.1.0 — Add Bollinger Bands indicator
```
