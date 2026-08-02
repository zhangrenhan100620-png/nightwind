from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from nightwind.audit import audit_repository
from nightwind.cli import main


class AuditRepositoryTests(unittest.TestCase):
    def test_empty_repository_reports_missing_controls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = audit_repository(directory)

        self.assertLess(report.score, report.max_score)
        self.assertTrue(any(f.rule_id == "docs.readme" and not f.passed for f in report.findings))
        self.assertEqual(100, report.max_score)

    def test_complete_repository_reaches_full_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_complete_repository(root)
            report = audit_repository(root)

        self.assertEqual(100, report.score)
        self.assertTrue(all(finding.passed for finding in report.findings))

    def test_secret_bearing_env_file_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("TOKEN=not-a-real-secret\n", encoding="utf-8")
            report = audit_repository(root)

        finding = next(f for f in report.findings if f.rule_id == "security.no_env_files")
        self.assertFalse(finding.passed)

    def test_sanitized_env_example_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text("TOKEN=\n", encoding="utf-8")
            report = audit_repository(root)

        finding = next(f for f in report.findings if f.rule_id == "security.no_env_files")
        self.assertTrue(finding.passed)

    def test_file_index_is_refreshed_between_audits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = audit_repository(root)
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            second = audit_repository(root)

        first_readme = next(f for f in first.findings if f.rule_id == "docs.readme")
        second_readme = next(f for f in second.findings if f.rule_id == "docs.readme")
        self.assertFalse(first_readme.passed)
        self.assertTrue(second_readme.passed)

    def test_json_cli_output_and_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main([directory, "--format", "json", "--fail-under", "100"])

        payload = json.loads(output.getvalue())
        self.assertEqual(1, exit_code)
        self.assertEqual("1", payload["schema_version"])
        self.assertEqual(100, payload["max_score"])

    @staticmethod
    def _write_complete_repository(root: Path) -> None:
        files = {
            "README.md": """# Example\n\n## Installation\n\n## Usage\n\n## Limitations\n\n## Roadmap\n""",
            "LICENSE": "MIT\n",
            "CONTRIBUTING.md": "Contribute\n",
            "CODE_OF_CONDUCT.md": "Be kind\n",
            "CHANGELOG.md": "Changes\n",
            "SUPPORT.md": "Support\n",
            "SECURITY.md": "Security\n",
            "pyproject.toml": "[project]\nname='example'\n",
            "tests/test_example.py": "def test_example(): pass\n",
            ".github/dependabot.yml": "version: 2\nupdates: []\n",
            ".github/workflows/ci.yml": "permissions:\n  contents: read\n",
            ".github/workflows/codeql.yml": "permissions:\n  contents: read\n",
            ".github/ISSUE_TEMPLATE/bug.yml": "name: Bug\n",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
