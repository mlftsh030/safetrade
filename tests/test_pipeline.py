"""Tests for the SafeTrade ELT pipeline.

They use a tiny made-up file (tests/fixtures/tiny_sheet_export.csv) with
fake names, so every rule can be checked by hand. Run with:  pytest -q
"""
from pathlib import Path

import pandas as pd
import pytest

from pipeline import config, extract, load, quality, transform

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_sheet_export.csv"


@pytest.fixture
def warehouse(tmp_path):
    """Run extract -> load -> transform on the fixture in a temporary folder."""
    landing, n = extract.extract(FIXTURE, "test_batch", tmp_path / "landing")
    con = load.connect(tmp_path / "test.duckdb")
    load.load(con, landing, "test_batch")
    transform.transform(con)
    yield con, landing, tmp_path
    con.close()


def staging_value(con, column, where):
    return con.execute(
        f"SELECT {column} FROM staging.stg_survey_responses WHERE {where}"
    ).fetchone()[0]


# ---------- EXTRACT ----------

def test_extract_removes_personal_data(warehouse):
    _, landing, _ = warehouse
    df = pd.read_csv(landing)
    for col in ["name", "phone", "scam_story", "trust_insight"]:
        assert col not in df.columns
    assert "Test Person" not in landing.read_text()


def test_extract_fixes_misspelled_header(warehouse):
    _, landing, _ = warehouse
    assert "stopped_using" in pd.read_csv(landing).columns


def test_response_id_is_stable():
    df = extract.normalise_headers(extract.read_source(FIXTURE))
    first = extract.add_response_id(df)["response_id"].tolist()
    second = extract.add_response_id(df)["response_id"].tolist()
    assert first == second
    assert len(set(first)) == len(first)


def test_extract_stops_if_a_column_is_missing(tmp_path):
    broken = tmp_path / "broken.csv"
    pd.read_csv(FIXTURE).drop(columns=["When Pay"]).to_csv(broken, index=False)
    with pytest.raises(ValueError, match="when_pay"):
        extract.extract(broken, "b", tmp_path / "landing")


# ---------- LOAD ----------

def test_load_twice_does_not_duplicate(warehouse):
    con, landing, _ = warehouse
    result = load.load(con, landing, "second_run")
    assert result["rows_inserted"] == 0
    assert con.execute("SELECT count(*) FROM raw.survey_responses").fetchone()[0] == 3
    assert con.execute("SELECT count(*) FROM raw.load_log").fetchone()[0] == 2


def test_raw_keeps_original_text(warehouse):
    con, _, _ = warehouse
    values = {r[0] for r in con.execute("SELECT safety_feeling FROM raw.survey_responses").fetchall()}
    assert "Very Unsafe" in values  # raw is never cleaned


# ---------- TRANSFORM ----------

def test_scam_answers_that_the_first_notebook_missed(warehouse):
    con, _, _ = warehouse
    assert staging_value(con, "scam_experience", "age_band = '25–34'") == "never_scammed"
    assert staging_value(con, "scam_experience", "marketplace_frequency = 'weekly'") == "scammed"


def test_r10_to_r20_is_its_own_band(warehouse):
    con, _, _ = warehouse
    row = con.execute(
        "SELECT fee_willingness, fee_estimate_rand FROM staging.stg_survey_responses "
        "WHERE marketplace_frequency = 'weekly'"
    ).fetchone()
    assert row == ("r10_to_r20", 15)


def test_percentage_fee_has_no_rand_estimate(warehouse):
    con, _, _ = warehouse
    assert staging_value(con, "fee_willingness", "marketplace_frequency = 'occasionally'") == "percentage"
    assert staging_value(con, "fee_estimate_rand", "marketplace_frequency = 'occasionally'") is None


def test_safety_score_and_capital_letters(warehouse):
    con, _, _ = warehouse
    assert staging_value(con, "safety_score", "marketplace_frequency = 'weekly'") == 1


def test_multi_choice_answers_are_split(warehouse):
    con, _, _ = warehouse
    concerns = con.execute(
        "SELECT concern FROM intermediate.int_response_concerns ORDER BY concern"
    ).fetchall()
    assert [c[0] for c in concerns] == ["fake_sellers", "meeting_strangers", "payment_fraud"]


def test_percentages_use_people_who_answered(warehouse):
    con, _, _ = warehouse
    # 2 of 3 people answered the features question; 1 of those 2 wants escrow.
    row = con.execute(
        "SELECT numerator, denominator FROM marts.mart_headline_metrics "
        "WHERE segment = 'all' AND metric = 'want_escrow'"
    ).fetchone()
    assert row == (1, 2)


def test_segments_split_marketplace_users(warehouse):
    con, _, _ = warehouse
    rows = dict(con.execute(
        "SELECT segment, count(*) FROM marts.fct_survey_responses GROUP BY segment"
    ).fetchall())
    assert rows == {"marketplace_users": 2, "non_users": 1}


# ---------- QUALITY CHECKS ----------

def test_quality_checks_pass_on_clean_data(warehouse):
    con, _, _ = warehouse
    assert not quality.has_errors(quality.run_checks(con))


def test_quality_check_catches_an_unknown_answer(warehouse):
    con, _, _ = warehouse
    con.execute("UPDATE raw.survey_responses SET scam_experience = 'Maybe?' WHERE age = '25–34'")
    transform.transform(con)
    results = {r.name: r for r in quality.run_checks(con)}
    assert not results["04_every_answer_mapped"].passed
    assert quality.has_errors(results.values())


# ---------- END TO END ON THE REAL (ANONYMISED) SAMPLE ----------

def test_full_run_on_sample(tmp_path):
    landing, n = extract.extract(config.SAMPLE_SOURCE, "sample", tmp_path / "landing")
    con = load.connect(tmp_path / "sample.duckdb")
    load.load(con, landing, "sample")
    transform.transform(con)
    assert n == 59
    assert not quality.has_errors(quality.run_checks(con))
    escrow = con.execute(
        "SELECT numerator, denominator FROM marts.mart_headline_metrics "
        "WHERE segment = 'all' AND metric = 'want_escrow'"
    ).fetchone()
    assert escrow == (45, 56)


def test_double_submission_is_left_out(tmp_path):
    """The same answers sent twice within 2 minutes count once."""
    df = pd.read_csv(FIXTURE, dtype=str)
    repeat = df.iloc[[0]].copy()
    repeat["Timestamp"] = "2026-04-13T08:00:14.000Z"   # 14 seconds later
    later = df.iloc[[0]].copy()
    later["Timestamp"] = "2026-04-13T08:30:00.000Z"    # 30 minutes later: kept
    path = tmp_path / "with_repeats.csv"
    pd.concat([df, repeat, later]).to_csv(path, index=False)

    landing, n = extract.extract(path, "b", tmp_path / "landing")
    con = load.connect(tmp_path / "w.duckdb")
    load.load(con, landing, "b")
    transform.transform(con)
    assert n == 5
    assert con.execute("SELECT count(*) FROM staging.stg_survey_responses").fetchone()[0] == 5
    assert con.execute("SELECT count(*) FROM marts.fct_survey_responses").fetchone()[0] == 4
    flagged = {r.name: r.failing_rows for r in quality.run_checks(con)}
    assert flagged["11_double_submissions"] == 1


# ---------- LINEAGE ----------

def test_lineage_finds_every_model_and_its_sources():
    from pipeline import lineage
    models = {m.name: m.reads for m in lineage.parse_models()}
    assert models["staging.stg_survey_responses"] == {"raw.survey_responses"}
    assert "marts.mart_concerns" in models and "marts.mart_features" in models  # two tables, one file
    assert models["marts.mart_validation_scorecard"] == {"marts.mart_headline_metrics"}


def test_lineage_model_order_is_valid():
    from pipeline import lineage
    assert lineage.check_order(lineage.parse_models()) == []


def test_lineage_catches_a_model_reading_a_later_table():
    from pipeline import lineage
    bad = [lineage.Model("staging.a", "x.sql", {"marts.b"})]
    assert lineage.check_order(bad) == ["staging.a reads marts.b, which is not built before it"]


def test_lineage_report_has_row_counts(warehouse):
    from pipeline import lineage
    con, _, tmp_path = warehouse
    text = lineage.write_lineage(con, tmp_path / "lineage.md").read_text()
    assert "```mermaid" in text
    assert "survey_responses<br/><b>3 rows</b>" in text
