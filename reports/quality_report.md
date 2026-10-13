# Data quality report

_Written by the pipeline on every run. Do not edit by hand._

**8 of 10 checks passed** · 0 errors · 2 warnings

| Check | Level | Result | Rows flagged | What it checks |
|---|---|---|---|---|
| `01_unique_response_id` | error | pass | 0 | Every response appears once in raw (no duplicates from re-runs). |
| `02_not_null_response_id` | error | pass | 0 | Every response has an ID. |
| `03_no_rows_lost_in_staging` | error | pass | 0 | Staging has the same number of rows as raw (nothing dropped or doubled). |
| `04_every_answer_mapped` | error | pass | 0 | Every single-choice answer maps to a known category (no 'unmapped'). This check would have caught the two bugs in the first notebook. |
| `05_safety_score_in_range` | error | pass | 0 | Safety score is between 1 and 5 when present. |
| `06_valid_timestamps` | error | pass | 0 | Every response has a submission time that is not in the future. |
| `07_multi_choice_options_known` | warn | pass | 0 | Every ticked concern or feature is a known option. A new option in the survey shows up here as 'other'. |
| `08_skipped_key_questions` | warn | warning | 2 | Responses that skipped a key question. Not an error (questions were optional), but worth knowing. |
| `09_non_users_in_sample` | warn | warning | 32 | People who never use Facebook Marketplace but answered the Marketplace scam question. They are not the target users, so results are also shown for Marketplace users only. |
| `10_percentages_valid` | error | pass | 0 | Every percentage in the marts is between 0 and 1. |
