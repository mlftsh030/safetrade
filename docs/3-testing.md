# 3. Testing

**Two kinds of tests: unit tests check the code works, data quality checks check the data is right. A pipeline needs both.**

| | Unit tests (pytest) | Data quality checks (SQL) |
|---|---|---|
| Question | Does my code do what I meant? | Is today's data safe to use? |
| Runs on | A tiny made-up file with 3 fake people | The real data, on every run |
| When it fails | Before I commit a change | During a run, and the report is not published |
| Where | `tests/test_pipeline.py` | `sql/tests/*.sql` |

## Unit tests: 21 tests, all passing

```bash
pytest -q
................                                                         [100%]
21 passed in 2.19s
```

The fixture `tests/fixtures/tiny_sheet_export.csv` has fake names and phone numbers, the misspelt header, capital-letter variants and every awkward answer, so each rule can be checked by hand.

| Area | What is tested |
|---|---|
| Extract | Personal data is removed and never written to disk · misspelt header is fixed · response IDs are stable and unique · a missing column stops the run |
| Load | Loading the same file twice adds 0 rows · the load log records both runs · raw data keeps the original text |
| Transform | A repeat sent within 2 minutes is left out, one sent 30 minutes later is kept · "Yes — it happened to me" and "No, Never" are mapped (the notebook missed both) · "R10 – R20" gets its own band · a percentage fee has no rand estimate · multi-choice cells split correctly · percentages use people who answered · segments split correctly |
| Quality | Clean data passes · an unknown answer makes the run fail |
| Lineage | Every model and its sources are found (including two tables built in one file) · the run order is valid · a model reading a later table is caught · the diagram shows row counts |
| End to end | The full sample runs, passes every error check, and gives 45 of 56 for escrow |

## Data quality checks: 11 checks

Each check is a SQL query that returns the rows that **break** a rule. No rows means pass.

| Check | Level | Rule |
|---|---|---|
| `01_unique_response_id` | error | No response is loaded twice |
| `02_not_null_response_id` | error | Every response has an ID |
| `03_no_rows_lost_in_staging` | error | Staging has exactly as many rows as raw |
| `04_every_answer_mapped` | error | Every answer maps to a known category |
| `05_safety_score_in_range` | error | Safety score is 1 to 5 |
| `06_valid_timestamps` | error | Every response has a time, not in the future |
| `07_multi_choice_options_known` | warn | No unknown concern or feature options |
| `08_skipped_key_questions` | warn | Lists responses that skipped key questions |
| `09_non_users_in_sample` | warn | Lists people who never use Marketplace |
| `10_percentages_valid` | error | Every percentage is between 0 and 1 |
| `11_double_submissions` | warn | Lists identical answers sent again within 2 minutes |

**Error** stops the run. **Warn** lets the run finish but writes the issue in `reports/quality_report.md`, because some problems are facts to know about, not mistakes to fix.

Latest result: [reports/quality_report.md](../reports/quality_report.md)

## Bugs the tests found

| Bug | Where | Effect | Caught by |
|---|---|---|---|
| "Yes — it happened to me" not mapped (13 people) | v1 notebook | The 13 people who were actually scammed had no category | Check 04, unit test |
| "No, Never" (capital N) not mapped (1 person) | v1 notebook | One person missing from "never scammed" | Check 04, unit test |
| "R10 – R20" counted as "low" (5 people) | v1 notebook | The text contains "r10", so it matched the R5–R10 rule first | Unit test |
| Two concerns and two features had no column | v1 notebook | "No recourse", "ratings" and "safe meetups" were never counted | Long-format design |
| Mixed denominators in the first README | first write-up | Some % were "of everyone", some "of those who answered" | Rule 6: every metric stores its denominator |
| 55% of respondents never use Marketplace | the survey sample | Results mixed target users with non-users | Check 09, then segments were added |
| The same answers submitted twice, 14 seconds apart | the survey sample | One person counted twice; the response ID didn't catch it because it includes the timestamp | Manual check, then rule + check 11 |

## Checking the numbers

After the rebuild, I checked the pipeline's numbers against the v1 notebook for every column where the notebook was correct. They match. Where they differ, it's one of the bugs above.
