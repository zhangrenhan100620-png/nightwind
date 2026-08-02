# Security policy

## Supported versions

Nightwind is pre-1.0. Security fixes are applied to the latest code on `main`; older alpha snapshots are not maintained as separate support lines.

## Reporting a vulnerability

Do not disclose a suspected vulnerability in a public issue, discussion, or pull request.

1. Open the repository's **Security** tab and use **Report a vulnerability** if private vulnerability reporting is available.
2. Include the affected revision, a minimal reproduction, impact, and any suggested mitigation.
3. If the private-reporting button is unavailable, open a public issue containing no vulnerability details and ask the maintainer to establish a private channel.

The maintainer targets an initial acknowledgement within 7 days. This is a best-effort target, not a guaranteed service-level agreement. Valid reports will be investigated, fixed on a private branch when appropriate, and disclosed after users have a reasonable opportunity to update.

## Scope and safe handling

Nightwind reads repository metadata and small text files locally. It does not execute code from the audited repository and does not make network requests. Do not pass a directory containing data that the current operating-system user is not authorized to read.

See [docs/security-model.md](docs/security-model.md) for trust boundaries, known limitations, and the review required before adding networked or AI-assisted behavior.
