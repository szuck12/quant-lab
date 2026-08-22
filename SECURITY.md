# Security Policy

## Supported Versions

Only the latest release receives security fixes:

| Version | Supported |
|---------|-----------|
| Latest release (see [CHANGELOG.md](CHANGELOG.md)) | Yes |
| Older releases | No |

## Reporting a Vulnerability

Please report suspected vulnerabilities privately through GitHub's
vulnerability reporting (Security tab -> Report a vulnerability) so
details stay confidential until a fix ships.

Please include:

- A description of the issue and its impact.
- Steps to reproduce, if possible.
- Any suggested fixes.

What happens next:

- Acknowledgement within 7 days.
- Assessment and, where applicable, a fix in the next PATCH release.
- Public disclosure after the fix ships, described in general terms.

## Disclosure Style

This project discusses security topics in general terms only across
its public artifacts (documentation, changelog, commit messages).
Specific technical details are handled privately between the
reporter and the maintainer until a fix is available.

## Scope Notes

QuantLab is a local command-line tool. It reads ticker input from
stdin or argv, fetches market data from Yahoo Finance through
yfinance over HTTPS, and prints results to stdout. It stores no
credentials, runs no servers, and executes no downloaded code.
