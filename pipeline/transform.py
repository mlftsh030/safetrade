"""TRANSFORM: run the SQL models inside the warehouse.

The SQL lives in sql/<layer>/ and runs layer by layer, files in name
order. Data only flows forward: a model reads its own layer or earlier ones.

    raw  ->  staging  ->  intermediate  ->  marts

Every model uses CREATE OR REPLACE, so running it again rebuilds the
same result from raw. Raw is never changed, so a mistake in cleaning
can be fixed and re-run without collecting the data again.
"""
from __future__ import annotations

from pathlib import Path

import duckdb

from pipeline import config


def model_files(sql_dir: Path = config.SQL_DIR) -> list[Path]:
    files: list[Path] = []
    for layer in config.TRANSFORM_LAYERS:
        files.extend(sorted((sql_dir / layer).glob("*.sql")))
    return files


def transform(con: duckdb.DuckDBPyConnection, sql_dir: Path = config.SQL_DIR) -> list[str]:
    """Run every model. Returns the list of models built, in order."""
    con.execute(f"SET VARIABLE willing_to_pay_threshold = {config.WILLING_TO_PAY_THRESHOLD}")
    built = []
    for path in model_files(sql_dir):
        con.execute(path.read_text(encoding="utf-8"))
        built.append(f"{path.parent.name}/{path.stem}")
    return built
