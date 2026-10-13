# 5. Learnings

**Each lesson comes from something that actually happened in this project, and what I changed because of it.**

| # | What happened | What I changed | What I do now |
|---|---|---|---|
| 1 | My first public repo had the survey file with real names and phone numbers in it | Personal data is now removed in the extract step, before anything is saved. The repo was rebuilt with clean history. | Decide what's personal data **before** collecting it, and remove it at the door |
| 2 | The first notebook missed 3 answer types (13 people who were scammed had no category) and nothing warned me | Every mapping ends in `ELSE 'unmapped'`, and a check fails the run if `'unmapped'` appears | Never let unknown data pass silently. Make it fail loudly. |
| 3 | `"R10 – R20"` was counted as "low" because the text contains `"r10"` | Match the start of the answer with a pattern (`^r10\s*[–-]\s*r20`), and give it its own band | Order and precision in matching rules matter; test the awkward cases |
| 4 | Some numbers in my first write-up were "% of everyone" and some "% of people who answered" | Every metric stores its numerator and denominator next to it | A percentage without "of whom" is not a fact |
| 5 | 55% of people who answered never use Facebook Marketplace | Results are now split into Marketplace users and non-users, and judged on users | Check **who** the data is about before trusting **what** it says |
| 6 | One of my own quality checks was wrong at first: I flagged people who "never" use Marketplace but "have bought online" as contradictions. The two questions ask different things (Marketplace vs any website) | Read the real question wording in the prototype and rewrote the check | Read the source before writing rules about it |
| 7 | When a cleaning rule was wrong in the notebook, the only fix was to read the whole sheet again | Moved to ELT: raw is stored once and never changed; SQL can be re-run any time | Keep the raw data. Cleaning is a step you will redo. |
| 8 | The same answers were submitted twice, 14 seconds apart. My duplicate check missed it, because the ID included the timestamp | Added a second fingerprint of the answers only, and a 2-minute rule | "No duplicates" depends on how you define the same thing. Decide the rule on purpose. |
| 9 | pandas turned phone numbers into scientific notation | Extract reads every value as text | Don't let a tool guess types; set them on purpose in staging |

## What I'd do next

| Next step | Why | Concept |
|---|---|---|
| Run on a schedule (GitHub Actions, daily) | New answers would appear without me starting it | Orchestration |
| Run tests on every push (GitHub Actions) | A broken change can't reach the main branch | CI/CD |
| Move the SQL into dbt | Built-in tests, docs and lineage graph for free | Analytics engineering |
| Build the demand-test page and load its clicks as a second source | Measures criterion 3, the last one | Multiple sources, joins |
| Track how answers change over time (a daily snapshot table) | See if concern grows as more people answer | Slowly changing data, snapshots |
| Add a simple dashboard on the marts | Non-technical people can explore it | BI layer |

## In one sentence

The hardest part was not the code; it was making sure the data was **about the right people, counted the right way, and safe to share**.
