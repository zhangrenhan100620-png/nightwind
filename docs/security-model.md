# Security model

## Assets

Nightwind aims to protect the confidentiality and integrity of the repository being audited, the maintainer's workstation, and machine-readable audit output.

## Trust boundaries

The target repository is untrusted input. Nightwind may inspect file names and read bounded UTF-8 text, but it must not import modules, execute commands, evaluate configuration, follow file symlinks, or send content to a network service.

Current safeguards include:

- no runtime dependencies;
- no network code;
- no subprocess or target-code execution;
- symlink skipping during traversal;
- a 512 KiB limit for text used in content checks;
- ignored build, dependency, VCS, cache, and virtual-environment directories;
- deterministic output with no embedded file contents.

## Known limitations

- File names and directory structure may still be sensitive when displayed in a local terminal or CI log.
- The auditor does not identify all secret formats and only flags likely `.env` files.
- Text-based workflow permission checks do not implement the complete YAML specification.
- Passing a rule proves only that a signal is present, not that its contents or enforcement are effective.
- Denial-of-service resistance for extremely large file trees is limited in the alpha release.

## Future networked or AI-assisted features

Any future feature that sends data off-device must be opt-in, document exactly what leaves the machine, minimize and redact content, provide a local-only alternative, and require human review before applying a change. Repository content must never be uploaded merely because an API key is present.
