"""Repository readiness checks used by the Nightwind CLI.

The auditor is intentionally conservative: it reports whether maintainability
signals are present, but it does not claim that a repository is secure, popular,
or important to an ecosystem.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import os
from pathlib import Path
import re
from typing import Callable, Iterable


MAX_TEXT_BYTES = 512 * 1024
IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
}


@dataclass(frozen=True)
class Finding:
    """The result of one repository readiness rule."""

    rule_id: str
    category: str
    passed: bool
    points: int
    max_points: int
    message: str
    remediation: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    """A deterministic summary of all Nightwind checks."""

    target: str
    score: int
    max_score: int
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, object]:
        """Return the stable public report schema."""

        return {
            "schema_version": "1",
            "target": self.target,
            "score": self.score,
            "max_score": self.max_score,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass(frozen=True)
class _Rule:
    rule_id: str
    category: str
    max_points: int
    success: str
    remediation: str
    check: Callable[[Path], bool]


@lru_cache(maxsize=1)
def _relative_files(root: Path) -> frozenset[str]:
    files: set[str] = set()
    for current, directories, names in os.walk(root, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES
            and not (Path(current) / name).is_symlink()
        ]
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.is_symlink():
                continue
            files.add(path.relative_to(root).as_posix().lower())
    return frozenset(files)


def _has_any_file(*candidates: str) -> Callable[[Path], bool]:
    lowered = {candidate.lower() for candidate in candidates}

    def check(root: Path) -> bool:
        return bool(_relative_files(root) & lowered)

    return check


def _read_small_text(path: Path) -> str:
    try:
        if path.is_symlink() or path.stat().st_size > MAX_TEXT_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


@lru_cache(maxsize=8)
def _find_case_insensitive(root: Path, relative_path: str) -> Path | None:
    wanted = relative_path.lower()
    for current, directories, names in os.walk(root, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES
            and not (Path(current) / name).is_symlink()
        ]
        current_path = Path(current)
        for name in names:
            path = current_path / name
            if path.is_symlink():
                continue
            if path.relative_to(root).as_posix().lower() == wanted:
                return path
    return None


def _readme_has_heading(*headings: str) -> Callable[[Path], bool]:
    alternatives = "|".join(re.escape(heading) for heading in headings)
    pattern = re.compile(rf"^\s*#{{1,6}}\s+(?:{alternatives})\b", re.IGNORECASE | re.MULTILINE)

    def check(root: Path) -> bool:
        readme = _find_case_insensitive(root, "README.md")
        return bool(readme and pattern.search(_read_small_text(readme)))

    return check


def _has_tests(root: Path) -> bool:
    return any(
        name.startswith("tests/test_") or name.endswith("_test.py")
        for name in _relative_files(root)
    )


def _has_issue_template(root: Path) -> bool:
    return any(
        name.startswith(".github/issue_template/")
        and name.endswith((".md", ".yml", ".yaml"))
        for name in _relative_files(root)
    )


def _has_explicit_workflow_permissions(root: Path) -> bool:
    github_root = root / ".github"
    workflow_root = root / ".github" / "workflows"
    if github_root.is_symlink() or workflow_root.is_symlink() or not workflow_root.is_dir():
        return False

    workflows = sorted(
        path
        for path in workflow_root.iterdir()
        if path.is_file() and not path.is_symlink() and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not workflows:
        return False

    for workflow in workflows:
        text = _read_small_text(workflow)
        if re.search(r"(?im)^\s*permissions\s*:\s*write-all\s*$", text):
            return False
        if not re.search(r"(?m)^permissions\s*:", text):
            return False
    return True


def _has_no_env_files(root: Path) -> bool:
    allowed = {".env.example", ".env.sample", ".env.template"}
    for relative in _relative_files(root):
        name = Path(relative).name
        if name == ".env" or (name.startswith(".env.") and name not in allowed):
            return False
    return True


RULES: tuple[_Rule, ...] = (
    _Rule(
        "docs.readme",
        "documentation",
        8,
        "README.md is present.",
        "Add a README that explains what the project does and who it serves.",
        _has_any_file("README.md"),
    ),
    _Rule(
        "docs.installation",
        "documentation",
        5,
        "README includes installation or getting-started guidance.",
        "Add an Installation or Getting started heading to README.md.",
        _readme_has_heading("installation", "getting started"),
    ),
    _Rule(
        "docs.usage",
        "documentation",
        5,
        "README includes usage or quick-start guidance.",
        "Add a Usage or Quick start heading with a runnable example.",
        _readme_has_heading("usage", "quick start"),
    ),
    _Rule(
        "docs.limitations",
        "documentation",
        4,
        "README states limitations or non-goals.",
        "Document what the project does not guarantee.",
        _readme_has_heading("limitations", "non-goals"),
    ),
    _Rule(
        "docs.roadmap",
        "documentation",
        3,
        "A roadmap or project-status section is present.",
        "Add a Roadmap or Project status section so expectations are clear.",
        _readme_has_heading("roadmap", "project status"),
    ),
    _Rule(
        "community.license",
        "community",
        8,
        "An open-source license file is present.",
        "Choose an OSI-approved license and add it as LICENSE.",
        _has_any_file("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
    ),
    _Rule(
        "community.contributing",
        "community",
        6,
        "Contribution guidelines are present.",
        "Add CONTRIBUTING.md with setup, testing, and review expectations.",
        _has_any_file("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"),
    ),
    _Rule(
        "community.code_of_conduct",
        "community",
        4,
        "A code of conduct is present.",
        "Add CODE_OF_CONDUCT.md and explain how incidents are handled.",
        _has_any_file("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md", "docs/CODE_OF_CONDUCT.md"),
    ),
    _Rule(
        "community.changelog",
        "community",
        4,
        "A changelog is present.",
        "Add CHANGELOG.md and record user-visible changes.",
        _has_any_file("CHANGELOG.md", "HISTORY.md"),
    ),
    _Rule(
        "community.support",
        "community",
        3,
        "Support guidance is present.",
        "Add SUPPORT.md describing where to ask questions and report bugs.",
        _has_any_file("SUPPORT.md", ".github/SUPPORT.md", "docs/SUPPORT.md"),
    ),
    _Rule(
        "security.policy",
        "security",
        8,
        "A vulnerability disclosure policy is present.",
        "Add SECURITY.md with private reporting and response expectations.",
        _has_any_file("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"),
    ),
    _Rule(
        "security.no_env_files",
        "security",
        6,
        "No likely secret-bearing .env file was found.",
        "Remove committed .env files, rotate exposed secrets, and keep only a sanitized example.",
        _has_no_env_files,
    ),
    _Rule(
        "security.dependency_updates",
        "security",
        5,
        "Dependabot configuration is present.",
        "Add .github/dependabot.yml for relevant package ecosystems.",
        _has_any_file(".github/dependabot.yml", ".github/dependabot.yaml"),
    ),
    _Rule(
        "security.code_scanning",
        "security",
        5,
        "A CodeQL workflow is present.",
        "Add a CodeQL workflow or enable GitHub's default code-scanning setup.",
        _has_any_file(".github/workflows/codeql.yml", ".github/workflows/codeql.yaml"),
    ),
    _Rule(
        "security.workflow_permissions",
        "security",
        6,
        "Every workflow declares top-level least-privilege permissions.",
        "Declare top-level permissions in every workflow and avoid write-all.",
        _has_explicit_workflow_permissions,
    ),
    _Rule(
        "automation.ci",
        "automation",
        8,
        "A continuous-integration workflow is present.",
        "Add .github/workflows/ci.yml and run the project's verification commands.",
        _has_any_file(".github/workflows/ci.yml", ".github/workflows/ci.yaml"),
    ),
    _Rule(
        "automation.tests",
        "automation",
        6,
        "Automated tests are present.",
        "Add tests that cover success, failure, and command-line behavior.",
        _has_tests,
    ),
    _Rule(
        "automation.manifest",
        "automation",
        3,
        "A package or build manifest is present.",
        "Add a standard package/build manifest for the project's ecosystem.",
        _has_any_file(
            "pyproject.toml",
            "package.json",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
        ),
    ),
    _Rule(
        "automation.issue_templates",
        "automation",
        3,
        "Issue templates are present.",
        "Add focused bug and feature issue templates under .github/ISSUE_TEMPLATE.",
        _has_issue_template,
    ),
)


def audit_repository(target: str | Path) -> AuditReport:
    """Audit *target* and return a deterministic readiness report.

    Args:
        target: Directory containing the repository to audit.

    Raises:
        ValueError: If *target* does not exist or is not a directory.
    """

    root = Path(target).expanduser()
    if not root.exists():
        raise ValueError(f"target does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"target is not a directory: {root}")
    root = root.resolve()
    _relative_files.cache_clear()
    _find_case_insensitive.cache_clear()

    findings: list[Finding] = []
    for rule in RULES:
        passed = rule.check(root)
        findings.append(
            Finding(
                rule_id=rule.rule_id,
                category=rule.category,
                passed=passed,
                points=rule.max_points if passed else 0,
                max_points=rule.max_points,
                message=rule.success if passed else rule.remediation,
                remediation=None if passed else rule.remediation,
            )
        )

    score = sum(finding.points for finding in findings)
    max_score = sum(finding.max_points for finding in findings)
    return AuditReport(
        target=str(root),
        score=score,
        max_score=max_score,
        findings=tuple(findings),
    )


def failed_findings(findings: Iterable[Finding]) -> tuple[Finding, ...]:
    """Return failed findings while preserving rule order."""

    return tuple(finding for finding in findings if not finding.passed)
