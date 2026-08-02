# Maintainer guide

## Triage

1. Confirm that a report contains no secrets or private repository content.
2. Reproduce bugs on a supported Python version.
3. Label the issue by impact and affected rule or interface.
4. Link duplicate reports and preserve the clearest reproduction.
5. Route security-sensitive reports to the private process in SECURITY.md.

## Pull-request review

- Confirm scope, tests, documentation, and changelog impact.
- Check that a new rule is objective, deterministic, and paired with concrete remediation.
- Treat a score change as a public API change when it can affect `--fail-under` users.
- Require human review for dependency, workflow-permission, release, and security-model changes.

## Release checklist

1. Ensure CI and CodeQL are green on the release commit.
2. Run the verification commands in AGENTS.md locally.
3. Move relevant changelog entries from Unreleased to the version and date.
4. Confirm package metadata and version agree.
5. Create release notes from the reviewed changelog; do not claim unverified usage or security guarantees.
