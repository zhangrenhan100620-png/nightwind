# Nightwind

[![CI](https://github.com/zhangrenhan100620-png/nightwind/actions/workflows/ci.yml/badge.svg)](https://github.com/zhangrenhan100620-png/nightwind/actions/workflows/ci.yml)
[![CodeQL](https://github.com/zhangrenhan100620-png/nightwind/actions/workflows/codeql.yml/badge.svg)](https://github.com/zhangrenhan100620-png/nightwind/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Nightwind is a small, dependency-free command-line auditor for open-source maintainers. It checks whether a repository exposes the documentation, community, security, and automation signals that contributors need before they can use or maintain a project confidently.

Nightwind reports evidence that is present in a repository. It does **not** invent usage metrics, certify security, or decide whether a project is important to an ecosystem.

## Project status

Nightwind is an early-stage `0.1.0-alpha` project. Local auditing, text output, JSON output, and score thresholds are usable now. The rules and JSON schema may change before `1.0`.

## Installation

Nightwind requires Python 3.10 or newer and has no runtime dependencies.

```bash
git clone https://github.com/zhangrenhan100620-png/nightwind.git
cd nightwind
python -m pip install -e .
```

## Usage

Audit the current repository:

```bash
nightwind .
```

Produce machine-readable output and fail CI when the score is below 80:

```bash
nightwind . --format json --fail-under 80
```

Run without installing the package:

```bash
PYTHONPATH=src python -m nightwind .
```

Exit codes are stable for automation:

| Code | Meaning |
|---:|---|
| `0` | The audit completed and met `--fail-under`. |
| `1` | The audit completed but did not meet the threshold. |
| `2` | Arguments or the target path were invalid. |

## What Nightwind checks

The initial rule set totals 100 points across four categories:

| Category | Examples | Points |
|---|---|---:|
| Documentation | README, installation, usage, limitations, status/roadmap | 25 |
| Community | License, contributing guide, code of conduct, changelog, support | 25 |
| Security | Disclosure policy, `.env` hygiene, Dependabot, CodeQL, workflow permissions | 30 |
| Automation | CI, tests, package manifest, issue templates | 20 |

Every failed rule includes a concrete remediation. Scores are a prioritization aid, not a quality or security certification.

## Limitations

- Nightwind checks repository contents, not GitHub settings, traffic, stars, downloads, or maintainer identity.
- It does not execute target code and is not a vulnerability scanner.
- Workflow permission checks are intentionally conservative text checks, not a full YAML semantic analysis.
- File-presence checks cannot prove that a policy is effective or that maintenance is active.
- Results should be reviewed by a human before changing release or security decisions.

See the [security model](docs/security-model.md) for trust boundaries and safe-use guidance.

## Development

Run the complete local verification suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m nightwind . --fail-under 100
```

Changes should include tests and user-facing documentation when behavior changes. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Roadmap

Planned work is deliberately separated from current functionality. Priorities include SARIF output, a documented configuration file, a reusable GitHub Action, and an opt-in human-reviewed remediation assistant. See [docs/roadmap.md](docs/roadmap.md) for scope and safety constraints.

## Security

Please do not post suspected vulnerabilities in a public issue. Follow [SECURITY.md](SECURITY.md) for private-reporting guidance and response expectations.

## Maintainer

Nightwind is currently maintained by [Renan Zhang](https://github.com/zhangrenhan100620-png). Governance is single-maintainer while the project is in alpha; contributor roles will be documented if the maintainer group grows.

## License

Nightwind is available under the [MIT License](LICENSE).
