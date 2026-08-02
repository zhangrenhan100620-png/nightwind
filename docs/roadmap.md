# Roadmap

This roadmap describes intent, not shipped functionality or delivery guarantees.

## 0.1: trustworthy local baseline

- Stabilize rule identifiers and JSON schema.
- Add performance limits for very large repository trees.
- Test supported Python versions and major operating systems.
- Publish a signed alpha release after CI and maintainer review.

## 0.2: maintainer workflow integration

- Add a documented configuration file with explicit ignore reasons.
- Add SARIF output for GitHub code-scanning interfaces.
- Package Nightwind as a reusable GitHub Action.
- Add regression fixtures for common open-source repository layouts.

## 0.3: opt-in remediation assistance

- Generate a remediation plan from failed rule identifiers without uploading source code by default.
- Evaluate an optional OpenAI API integration for summarizing findings and drafting human-reviewed maintenance changes.
- Publish privacy, prompt-injection, cost-control, and failure-mode tests before enabling any networked path.

Priorities will be adjusted from reproducible issues and contributor feedback, not fabricated adoption signals.
