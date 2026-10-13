"""LOAD: copy the landing snapshot into the warehouse, as it is.

The warehouse is a DuckDB file: a small database built for analysis
that runs on a laptop with no server. Raw data goes into the `raw`
schema, with every value still text.

Two rules make the load safe to run again and again ("idempotent"):
- a response is only inserted if its response_id is not already there;
- every load is written to raw.load_log, so we can see what each run did.
"""
from __future__ import annotations

from pathlib import Path

import duckdb

from pipeline import config

ANSWER_COLUMNS = ", ".join(f"{c} VARCHAR" for c in config.EXPECTED_COLUMNS)


def connect(db_path: Path = config.WAREHOUSE_PATH) -> duckdb.DuckDBPyConnection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def create_raw_tables(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS raw.survey_responses (
            response_id VARCHAR,
            {ANSWER_COLUMNS},
            _batch_id   VARCHAR,
            _loaded_at  TIMESTAMP,
            _source     VARCHAR
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.load_log (
            batch_id      VARCHAR,
            source_file   VARCHAR,
            rows_in_file  INTEGER,
            rows_inserted INTEGER,
            loaded_at     TIMESTAMP
        )
    """)


def load(con: duckdb.DuckDBPyConnection, landing_file: Path, batch_id: str) -> dict:
    """Insert only new responses. Returns counts for the run log."""
    create_raw_tables(con)
    columns = ", ".join(["response_id", *config.EXPECTED_COLUMNS])
    before = con.execute("SELECT count(*) FROM raw.survey_responses").fetchone()[0]

    con.execute(
        f"""
        INSERT INTO raw.survey_responses
        SELECT {columns}, ? AS _batch_id, now()::TIMESTAMP, ? AS _source
        FROM read_csv(?, header = true, all_varchar = true) AS src
        WHERE src.response_id NOT IN (SELECT response_id FROM raw.survey_responses)
        QUALIFY row_number() OVER (PARTITION BY src.response_id) = 1
        """,
        [batch_id, Path(landing_file).name, str(landing_file)],
    )

    after = con.execute("SELECT count(*) FROM raw.survey_responses").fetchone()[0]
    rows_in_file = con.execute(
        "SELECT count(*) FROM read_csv(?, header = true, all_varchar = true)",
        [str(landing_file)],
    ).fetchone()[0]
    inserted = after - before
    con.execute(
        "INSERT INTO raw.load_log VALUES (?, ?, ?, ?, now()::TIMESTAMP)",
        [batch_id, Path(landing_file).name, rows_in_file, inserted],
    )
    return {"rows_in_file": rows_in_file, "rows_inserted": inserted, "rows_total": after}
