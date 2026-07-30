# Security policy

## Reporting a problem

Use GitHub's private vulnerability-reporting feature for this repository, or
contact a maintainer through an already established private channel. Do not put
credentials, subscriber data, private packet captures, or exploitable lab
details in a public issue.

## Repository rules

- Use SSH keys or an institution-approved credential manager.
- Never commit passwords, API keys, SIM credentials, WireGuard private keys,
  `.env` files, or live subscriber identifiers.
- Sanitize packet captures and screenshots before sharing them.
- Treat credentials found in any Git commit as compromised even if they were
  removed from the latest revision.
- Use documentation address ranges and placeholders for examples where the
  exact lab topology is not essential.

## Known history exposure

An audit on 29 July 2026 found plaintext lab credentials in earlier commits.
They have been removed from the current working tree, but Git history retains
old file contents until maintainers rewrite it. The affected credentials must be
rotated, history must be rewritten across all branches and tags, and existing
clones or forks must be treated as retaining the old data.

Removing a secret in a new commit is not sufficient remediation.

