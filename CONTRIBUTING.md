# Contributing to Nightwind

Thank you for helping improve Nightwind. The project favors small, reviewable changes backed by evidence and tests.

## Before you start

- Search existing issues and pull requests to avoid duplicate work.
- Use a bug report for incorrect behavior and a feature request for proposed scope.
- For a substantial rule or report-schema change, open an issue before implementation.
- Report suspected vulnerabilities through the process in [SECURITY.md](SECURITY.md), not a public issue.

## Local setup

Nightwind requires Python 3.10 or newer and has no runtime dependencies.

```bash
git clone https://github.com/zhangrenhan100620-png/nightwind.git
cd nightwind
python -m pip install -e .
```

## Verification

Run both commands before submitting a pull request:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m nightwind . --fail-under 100
```

New behavior should include tests for a passing case, a failing case, and relevant command-line output. Avoid adding a runtime dependency unless the benefit and supply-chain cost are documented in the pull request.

## Pull requests

- Keep the change focused and explain the user or maintainer impact.
- Update README, changelog, and security model when behavior or trust boundaries change.
- Do not claim adoption, downloads, security guarantees, or ecosystem impact without a link to verifiable evidence.
- Do not commit credentials, personal data, generated environments, or local configuration.
- Expect review feedback before merge. Passing CI is necessary but not sufficient for acceptance.

By contributing, you agree that your contribution is licensed under the repository's MIT License.
