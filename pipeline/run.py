"""Run the whole pipeline:  python -m pipeline.run

    python -m pipeline.run                 # use the anonymised sample in data/sample/
    python -m pipeline.run --source sheet  # use the live Google Sheet (needs SAFETRADE_SHEET_URL)
    python -m pipeline.run --source path/to/export.csv

Steps: extract -> load -> transform -> quality checks -> report -> lineage diagram.
If an error-level quality check fails, the run stops before the report,
so wrong numbers are never published.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time

from pipeline import config, extract, lineage, load, quality, report, transform

log = logging.getLogger("safetrade")


def resolve_source(source: str) -> str:
    if source == "sample":
        return str(config.SAMPLE_SOURCE)
    if source == "sheet":
        url = os.environ.get(config.SHEET_URL_ENV)
        if not url:
            sys.exit(f"Set {config.SHEET_URL_ENV} to the sheet's CSV export link first.")
        return url
    return source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SafeTrade ELT pipeline")
    parser.add_argument("--source", default="sample", help="'sample', 'sheet', or a CSV path")
    parser.add_argument("--db", default=str(config.WAREHOUSE_PATH), help="DuckDB file")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-5s  %(message)s",
                        datefmt="%H:%M:%S")

    started = time.perf_counter()
    batch_id = extract.new_batch_id()
    source = resolve_source(args.source)
    log.info("Batch %s, source: %s", batch_id, "Google Sheet" if args.source == "sheet" else source)

    landing, rows = extract.extract(source, batch_id)
    log.info("EXTRACT    %d responses -> %s (personal data removed)", rows, landing.relative_to(config.ROOT))

    con = load.connect(args.db)
    counts = load.load(con, landing, batch_id)
    log.info("LOAD       %d new, %d already loaded, %d in raw",
             counts["rows_inserted"], counts["rows_in_file"] - counts["rows_inserted"], counts["rows_total"])

    order_problems = lineage.check_order(lineage.parse_models())
    if order_problems:
        for problem in order_problems:
            log.error("ORDER      %s", problem)
        return 1
    built = transform.transform(con)
    log.info("TRANSFORM  built %d models: %s", len(built), ", ".join(built))

    results = quality.run_checks(con)
    quality.write_report(results, config.REPORTS_DIR / "quality_report.md")
    for r in results:
        if not r.passed:
            level = logging.ERROR if r.severity == "error" else logging.WARNING
            log.log(level, "CHECK      %s: %d rows flagged", r.name, r.failing_rows)
    passed = sum(r.passed for r in results)
    log.info("CHECKS     %d of %d passed", passed, len(results))
    if quality.has_errors(results):
        log.error("Stopped: an error-level check failed. See reports/quality_report.md")
        return 1

    out = report.write_report(con)
    log.info("REPORT     %s", out.relative_to(config.ROOT))
    log.info("LINEAGE    %s", lineage.write_lineage(con).relative_to(config.ROOT))
    log.info("Done in %.1fs", time.perf_counter() - started)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
