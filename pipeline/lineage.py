"""LINEAGE: draw the pipeline from the code itself.

Reads every SQL model, finds which table it builds and which tables it
reads (FROM / JOIN), and writes a Mermaid diagram to
reports/lineage.md, with the row count of every table from the latest
run. GitHub draws Mermaid diagrams automatically.

Because the diagram is built from the SQL, it can never go out of date:
add a model and it appears on the next run.

    python -m pipeline.lineage      # print the diagram for the current warehouse
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

from pipeline import config

LAYERS = ["raw", *config.TRANSFORM_LAYERS]
TABLE = r"(?:raw|staging|intermediate|marts)\.\w+"
BUILDS = re.compile(rf"CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?({TABLE})", re.I)
READS = re.compile(rf"(?:FROM|JOIN)\s+({TABLE})", re.I)


@dataclass
class Model:
    name: str                  # e.g. "staging.stg_survey_responses"
    file: str                  # e.g. "sql/staging/01_stg_survey_responses.sql"
    reads: set[str] = field(default_factory=set)

    @property
    def layer(self) -> str:
        return self.name.split(".")[0]


def _strip_comments(sql: str) -> str:
    return re.sub(r"--[^\n]*", "", sql)


def parse_models(sql_dir: Path = config.SQL_DIR) -> list[Model]:
    """One Model per table built. A file can build more than one table."""
    models: list[Model] = []
    for layer in config.TRANSFORM_LAYERS:
        for path in sorted((sql_dir / layer).glob("*.sql")):
            for statement in _strip_comments(path.read_text(encoding="utf-8")).split(";"):
                built = BUILDS.search(statement)
                if not built:
                    continue
                name = built.group(1).lower()
                reads = {t.lower() for t in READS.findall(statement)} - {name}
                models.append(Model(name, str(path.relative_to(config.ROOT)), reads))
    return models


def parse_checks(tests_dir: Path = config.SQL_DIR / "tests") -> dict[str, set[str]]:
    """Which tables each quality check reads."""
    return {
        p.stem: {t.lower() for t in READS.findall(_strip_comments(p.read_text(encoding="utf-8")))}
        for p in sorted(tests_dir.glob("*.sql"))
    }


def check_order(models: list[Model]) -> list[str]:
    """Problems with the run order: a model that reads a table not built
    before it. Empty list = the order is valid."""
    built = {"raw.survey_responses", "raw.load_log"}
    problems = []
    for m in models:
        for src in sorted(m.reads - built):
            problems.append(f"{m.name} reads {src}, which is not built before it")
        built.add(m.name)
    return problems


def row_counts(con: duckdb.DuckDBPyConnection, tables: set[str]) -> dict[str, int]:
    counts = {}
    for t in tables:
        try:
            counts[t] = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        except duckdb.Error:
            pass
    return counts


def _node_id(name: str) -> str:
    return name.replace(".", "__")


def to_mermaid(models: list[Model], counts: dict[str, int] | None = None,
               checks: dict[str, set[str]] | None = None) -> str:
    counts = counts or {}
    tables = {"raw.survey_responses"} | {m.name for m in models}
    lines = ["flowchart LR"]
    lines.append('    sheet[("Google Sheet<br/>survey answers")]')
    lines.append('    landing["Landing snapshot<br/>personal data removed"]')
    lines.append("    sheet -->|extract| landing")
    for layer in LAYERS:
        members = sorted(t for t in tables if t.startswith(layer + "."))
        if not members:
            continue
        lines.append(f'    subgraph {layer}["{layer}"]')
        for t in members:
            label = t.split(".", 1)[1]
            if t in counts:
                label += f"<br/><b>{counts[t]:,} rows</b>"
            lines.append(f'        {_node_id(t)}["{label}"]')
        lines.append("    end")
    lines.append(f"    landing -->|load| {_node_id('raw.survey_responses')}")
    for m in models:
        for src in sorted(m.reads):
            lines.append(f"    {_node_id(src)} --> {_node_id(m.name)}")
    if checks:
        lines.append(f'    checks{{{{"{len(checks)} quality checks"}}}}')
        lines.append("    marts -.-> checks")
        lines.append('    report[["Findings report<br/>+ charts"]]')
        lines.append("    checks -->|all errors pass| report")
    for layer in LAYERS:
        if any(t.startswith(layer + ".") for t in tables):
            lines.append(f"    style {layer} fill:#f7f9f8,stroke:#cfd6d2,color:#4a514e")
    lines += [
        "    classDef default fill:#ffffff,stroke:#7a807d,color:#111514",
        "    classDef src fill:#eef2f0,stroke:#7a807d,color:#111514",
        "    classDef mart fill:#dff3e8,stroke:#0b5a3a,color:#0b3d2c",
        "    class sheet,landing src",
    ]
    marts = [_node_id(t) for t in sorted(tables) if t.startswith("marts.")]
    if marts:
        lines.append(f"    class {','.join(marts)} mart")
    return "\n".join(lines)


def write_lineage(con: duckdb.DuckDBPyConnection, path: Path = config.REPORTS_DIR / "lineage.md") -> Path:
    models = parse_models()
    checks = parse_checks()
    tables = {"raw.survey_responses"} | {m.name for m in models}
    counts = row_counts(con, tables)
    diagram = to_mermaid(models, counts, checks)

    rows = ["| Table | Built by | Reads from | Rows |", "|---|---|---|---|",
            f"| raw.survey_responses | `pipeline/load.py` | landing snapshot | {counts.get('raw.survey_responses', '–')} |"]
    for m in models:
        rows.append(f"| {m.name} | `{m.file}` | {', '.join(sorted(m.reads))} | {counts.get(m.name, '–')} |")

    text = "\n".join([
        "# Pipeline lineage",
        "",
        "_Drawn by `pipeline/lineage.py` from the SQL files, with row counts from the latest run. Do not edit by hand._",
        "",
        "```mermaid",
        diagram,
        "```",
        "",
        "Arrows show which table each model reads. Data only flows forward: every model reads "
        "tables from its own layer or an earlier one, built before it runs (the pipeline checks this before transforming).",
        "",
        *rows,
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


if __name__ == "__main__":
    con = duckdb.connect(str(config.WAREHOUSE_PATH), read_only=True) if config.WAREHOUSE_PATH.exists() else None
    models = parse_models()
    print(to_mermaid(models, row_counts(con, {m.name for m in models} | {"raw.survey_responses"}) if con else None,
                     parse_checks()))
