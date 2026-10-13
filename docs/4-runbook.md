# 4. Runbook

**How to run, change, fix and hand over the pipeline. Written so someone else can do it without asking me.**

## Set up (once)

Needs Python 3.10 or newer.

```bash
git clone https://github.com/mlftsh030/safetrade.git
cd safetrade
pip install -r requirements.txt
pytest -q                     # should say: 21 passed
```

## Run

| Goal | Command |
|---|---|
| Run on the anonymised sample | `python -m pipeline.run` |
| Run on the live Google Sheet | see below |
| Run on a CSV export you downloaded | `python -m pipeline.run --source path/to/export.csv` |
| Start from scratch | delete `data/warehouse/` and `data/landing/`, then run again |

**Live sheet.** The sheet link is private and never goes in the code. In Google Sheets: File → Share → Publish to web → choose the responses tab and CSV, copy the link. Then:

```bash
export SAFETRADE_SHEET_URL="<the CSV link>"      # Windows PowerShell: $env:SAFETRADE_SHEET_URL="<link>"
python -m pipeline.run --source sheet
```

Only publish the sheet for as long as you need it, and turn publishing off afterwards.

## Run with Docker

Docker packs Python, the packages and the code into one **image**, so the pipeline runs the same way on any computer, with nothing to install except Docker.

```bash
docker build -t safetrade .                     # once, and again after changing code
```

| Goal | Command |
|---|---|
| Run on the sample, save the reports to your folder | `docker run --rm -v "$(pwd)/reports:/app/reports" safetrade` |
| Also keep the warehouse between runs | add `-v "$(pwd)/data/warehouse:/app/data/warehouse"` |
| Run the tests | `docker run --rm safetrade pytest -q` |
| Run on the live sheet | `docker run --rm -e SAFETRADE_SHEET_URL="<link>" -v "$(pwd)/reports:/app/reports" safetrade python -m pipeline.run --source sheet` |
| Look around inside | `docker run --rm -it safetrade bash` |

- `--rm` deletes the container when it finishes. `-v` connects a folder on your computer to a folder in the container, so the reports land on your computer.
- **Windows PowerShell:** use `${PWD}` instead of `$(pwd)`.
- **Linux, "Permission denied" on reports/:** the container runs as user 1000. Add `--user "$(id -u):$(id -g)"`.
- The image never contains real survey data: `.dockerignore` keeps `data/landing`, `data/warehouse` and reports out, and only the anonymised sample is copied in.

## What a good run looks like

- `LOAD` shows new rows the first time, and `0 new` if nothing changed.
- `CHECKS` has no ERROR lines. Warnings 08, 09 and 11 are expected.
- `reports/findings.md`, `reports/quality_report.md` and `reports/charts/*.png` are updated, and `reports/lineage.md` is redrawn.

To refresh the lineage **image** in the README (optional, needs Node.js): `npx @mermaid-js/mermaid-cli -i lineage.mmd -o docs/images/pipeline-lineage.png -b white -w 2000 -s 2`, where `lineage.mmd` is the diagram copied out of `reports/lineage.md`. GitHub already draws `reports/lineage.md` itself, so this is only for the picture.

## Common problems

| Message | Cause | Fix |
|---|---|---|
| `Source is missing expected columns: [...]` | A survey question was renamed or removed | Rename it back, or update `EXPECTED_COLUMNS` in `pipeline/config.py` and the staging SQL |
| `CHECK 04_every_answer_mapped: N rows flagged` (ERROR) | An answer option changed or was added | Look at `reports/quality_report.md`, then add a `WHEN ... LIKE ...` line in `sql/staging/01_stg_survey_responses.sql` |
| `CHECK 07_multi_choice_options_known` warning | A new concern or feature option | Add a `WHEN` line in the matching `sql/intermediate/` file |
| `Set SAFETRADE_SHEET_URL ...` | The link isn't set in this terminal | Run the `export` line again |
| HTTP 401 / 404 reading the sheet | The sheet isn't published, or the link is wrong | Re-publish as CSV and copy the link again |
| `LOAD 0 new` but you expected new answers | The landing file was the same as last time | Check the sheet has new rows; this is the dedupe working correctly |
| A number looks wrong | — | Check the layers in reverse: marts → intermediate → staging → raw. `raw` is the truth of what was received. |

To look inside the warehouse:

```bash
python -c "import duckdb; c=duckdb.connect('data/warehouse/safetrade.duckdb'); print(c.sql('SELECT * FROM marts.mart_headline_metrics'))"
```

## Change something

**Add a new single-choice question**
1. Add the column name to `EXPECTED_COLUMNS` in `pipeline/config.py`.
2. Delete `data/warehouse/`, so the raw table is rebuilt with the new column on the next run. (Raw is rebuilt from the source, so nothing is lost; the load log starts again.)
3. Map it in `sql/staging/01_stg_survey_responses.sql`, ending with `ELSE 'unmapped'`.
4. Add it to `sql/marts/01_fct_survey_responses.sql` and to the `UNION ALL` list in `02_mart_question_breakdown.sql`.
5. Add a unit test with an example answer, then run `pytest -q` and the pipeline.

**Add a new quality check**
Create `sql/tests/11_<name>.sql` that returns the rows breaking the rule, with these two header lines:
```sql
-- severity: error
-- description: What this rule means, in one sentence.
```

**Change the willing-to-pay bar**
Edit `WILLING_TO_PAY_THRESHOLD` in `pipeline/config.py`. It's an assumption, so write down why you changed it.

## Privacy rules (do not skip)

- Never commit a file with names, phone numbers or written stories. `data/landing/` and `data/warehouse/` are in `.gitignore` for this reason.
- If a new question collects personal data, add its column name to `PII_COLUMNS` in `pipeline/config.py` **before** the first run.
- Keep the Google Sheet restricted. Publish it to CSV only while running, then turn it off.

## Handover checklist

- [ ] Access to the Google Sheet and the Apps Script that receives answers
- [ ] Access to the Netlify site for the survey prototype
- [ ] This repo cloned, `pytest -q` passing
- [ ] One successful run on the live sheet
- [ ] Read `docs/1-design.md` (the rules) before changing anything
