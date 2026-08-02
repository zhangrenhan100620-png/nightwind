# Repository instructions

These instructions apply to the entire Nightwind repository.

## Product boundary

Nightwind is a local, dependency-free repository readiness auditor. It reports observable evidence; it must not claim that a repository is secure, popular, eligible for a program, or important to an ecosystem.

## Architecture

- `src/nightwind/audit.py`: deterministic rules and report schema.
- `src/nightwind/cli.py`: argument parsing, rendering, and exit codes.
- `tests/`: standard-library `unittest` coverage.
- `docs/security-model.md`: trust boundaries that must stay synchronized with behavior.

## Required verification

Run both commands after code, rule, workflow, or packaging changes:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m nightwind . --fail-under 100
```

## Change rules

- Preserve Python 3.10 compatibility and avoid runtime dependencies by default.
- Keep JSON output deterministic and backward-compatible within a documented schema version.
- Add or update tests for behavior changes.
- Never execute files from the audited repository or send repository contents over a network.
- Do not weaken workflow permissions or add secret-bearing examples.
- Update README, changelog, and security model when their statements change.
