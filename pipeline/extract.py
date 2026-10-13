"""EXTRACT: get the survey answers out of the source and save a snapshot.

Steps:
1. Read the source (the live Google Sheet, or the local sample file).
2. Tidy the column names so they are predictable.
3. Remove personal data (PII) straight away.
4. Give every response a stable ID, so re-runs don't create duplicates.
5. Save an unchanged snapshot to data/landing/ (the "landing zone").

Extract does NOT clean the answers. Cleaning happens later, in SQL. That
is the "ELT" idea: load the raw data first, transform it afterwards.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pipeline import config


def read_source(source: str | Path) -> pd.DataFrame:
    """Read a CSV from a file path or a URL. Every value is kept as text,
    so nothing is changed by accident (e.g. phone numbers turning into
    scientific notation, which happened in the first notebook)."""
    return pd.read_csv(source, dtype=str, keep_default_na=False, na_values=[""])


def normalise_headers(df: pd.DataFrame) -> pd.DataFrame:
    """'Top Concerns ' -> 'top_concerns', and fix known spelling mistakes."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)
    )
    return df.rename(columns=config.HEADER_FIXES)


def drop_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that identify a person, before anything is saved."""
    return df.drop(columns=[c for c in df.columns if c in config.PII_COLUMNS])


def check_columns(df: pd.DataFrame) -> None:
    """Stop early if the source has changed shape (a "schema check")."""
    missing = [c for c in config.EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Source is missing expected columns: {missing}")


def add_response_id(df: pd.DataFrame) -> pd.DataFrame:
    """Build an ID from the answers themselves (a "content hash").

    The same submission always gets the same ID, so if the sheet is read
    twice, the load step can see it already has that row.
    """
    df = df.copy()
    joined = df[config.EXPECTED_COLUMNS].fillna("").astype(str).agg("|".join, axis=1)
    df.insert(
        0,
        "response_id",
        joined.map(lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]),
    )
    return df


def new_batch_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def extract(source: str | Path, batch_id: str | None = None,
            landing_dir: Path = config.LANDING_DIR) -> tuple[Path, int]:
    """Run the extract step. Returns the snapshot path and the row count."""
    batch_id = batch_id or new_batch_id()
    df = read_source(source)
    df = normalise_headers(df)
    df = drop_pii(df)
    check_columns(df)
    df = add_response_id(df[config.EXPECTED_COLUMNS])

    landing_dir.mkdir(parents=True, exist_ok=True)
    path = landing_dir / f"responses_{batch_id}.csv"
    df.to_csv(path, index=False)
    return path, len(df)
