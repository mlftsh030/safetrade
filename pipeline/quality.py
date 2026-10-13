"""QUALITY CHECKS: prove the data is right before anyone uses it.

Each file in sql/tests/ is a query that returns the rows that BREAK a
rule. No rows = the check passes. Two levels:
- error: the run fails, and the report should not be trusted;
- warn:  the run continues, but the issue is written in the report.

The results are written to reports/quality_report.md on every run.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import duckdb

from pipeline import config

TESTS_DIR = config.SQL_DIR / "tests"


@dataclass
class CheckResult:
    name: str
    severity: str
    description: str
    failing_rows: int

    @property
    def passed(self) -> bool:
        return self.failing_rows == 0


def _header(sql: str, key: str, default: str = "") -> str:
    match = re.search(rf"--\s*{key}:\s*(.+)", sql)
    return match.group(1).strip() if match else default


def run_checks(con: duckdb.DuckDBPyConnection, tests_dir: Path = TESTS_DIR) -> list[CheckResult]:
    results = []
    for path in sorted(tests_dir.glob("*.sql")):
        sql = path.read_text(encoding="utf-8")
        failing = con.execute(f"SELECT count(*) FROM ({sql.rstrip().rstrip(';')})").fetchone()[0]
        results.append(CheckResult(
            name=path.stem,
            severity=_header(sql, "severity", "error"),
            description=_header(sql, "description"),
            failing_rows=failing,
        ))
    return results


def write_report(results: list[CheckResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    errors = [r for r in results if not r.passed and r.severity == "error"]
    warns = [r for r in results if not r.passed and r.severity == "warn"]
    lines = [
        "# Data quality report",
        "",
        "_Written by the pipeline on every run. Do not edit by hand._",
        "",
        f"**{sum(r.passed for r in results)} of {len(results)} checks passed** · "
        f"{len(errors)} errors · {len(warns)} warnings",
        "",
        "| Check | Level | Result | Rows flagged | What it checks |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        result = "pass" if r.passed else ("FAIL" if r.severity == "error" else "warning")
        lines.append(f"| `{r.name}` | {r.severity} | {result} | {r.failing_rows} | {r.description} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def has_errors(results: list[CheckResult]) -> bool:
    return any(not r.passed and r.severity == "error" for r in results)
