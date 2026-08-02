"""Command-line interface for Nightwind."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from . import __version__
from .audit import AuditReport, audit_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nightwind",
        description="Audit an open-source repository for maintainability and security-readiness signals.",
    )
    parser.add_argument("path", nargs="?", default=".", help="repository directory (default: current directory)")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="report format (default: text)",
    )
    parser.add_argument(
        "--fail-under",
        type=_score_threshold,
        default=0,
        metavar="SCORE",
        help="exit with status 1 when the score is below 0-100 SCORE",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _score_threshold(value: str) -> int:
    try:
        score = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer from 0 to 100") from exc
    if not 0 <= score <= 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return score


def _render_text(report: AuditReport) -> str:
    lines = [
        f"Nightwind audit: {report.target}",
        f"Score: {report.score}/{report.max_score}",
        "",
    ]
    for finding in report.findings:
        status = "PASS" if finding.passed else "FAIL"
        lines.append(
            f"[{status}] {finding.rule_id} "
            f"({finding.points}/{finding.max_points}) - {finding.message}"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = audit_repository(Path(args.path))
    except ValueError as exc:
        parser.error(str(exc))

    if args.output_format == "json":
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(_render_text(report))

    return 0 if report.score >= args.fail_under else 1


if __name__ == "__main__":
    sys.exit(main())
