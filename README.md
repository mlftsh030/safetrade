# SafeTrade

**Do people in South Africa want a safer way to buy and sell on Facebook Marketplace, and would they pay for it?**

SafeTrade started after a bad purchase of my own. Before building a payment platform, I tested the idea with a survey prototype and a Python/SQL **ELT pipeline**. The pipeline removes direct identifiers, loads the answers into DuckDB, checks data quality and produces findings against my [original proposal](docs/FirstProposal.pdf).
ac
**Status:** paused, October 2026. The survey supports two criteria; actual demand and sustainable delivery remain untested. I am not building or operating an escrow service.

- [Survey prototype](https://safetradesa.netlify.app/)
- [Findings and decision](docs/findings-and-decision.md)
- [Generated results and denominators](reports/findings.md)

## What I found

The public sample contains **59 submissions**. The duplicate heuristic flags one, leaving **58 analysed submissions: 26 Marketplace users and 32 non-users**. These are survey records, not independently verified unique people.

| Finding | Marketplace users who answered | All respondents who answered |
|---|---|---|
| Feel unsafe or very unsafe | **15/26 (58%)** | 35/57 (61%) |
| Were scammed or nearly scammed | **13/26 (50%)** | 17/57 (30%) |
| Cancelled a deal because they felt unsafe | **16/25 (64%)** | 25/56 (45%) |
| Want money held until the item arrives | **20/25 (80%)** | 45/56 (80%) |
| Would pay some fee for a safer transaction | **23/25 (92%)** | 48/56 (86%) |

Percentages are rounded. Each denominator includes only the records that answered that question, so it can be smaller than the segment size. The sample is small and self-selected, and the story shown before the survey may have influenced answers. These results do not establish national demand.

![Marketplace users compared with non-users](reports/charts/users_vs_non_users.png)

## Why I paused

The proposal asks whether people are concerned about safety, would pay a fee and take an observable action such as clicking a "Pay securely" option. The survey addresses the first two. For willingness to pay, I explicitly chose 50% as the working threshold because the proposal did not give one. The third criterion was not tested.

Stated interest is not proof that people would trust a new platform with their money. The fees people selected may not cover operating costs. I therefore paused the product while retaining the pipeline, evidence and conditions for reconsidering it. The [decision note](docs/findings-and-decision.md) explains the limitations and separates this decision from the earlier study's recommendation to continue testing.

## What I built

| Step | Implementation | Evidence |
|---|---|---|
| Extract | Read CSV, remove direct identifiers/free-text stories, assign stable IDs | [extract.py](pipeline/extract.py) |
| Load | Keep original answer values; skip already-loaded IDs | [load.py](pipeline/load.py) |
| Transform | Clean and reshape with eight SQL files across staging, intermediate and marts | [SQL models](sql/) |
| Duplicate review | Flag identical answer sets submitted within 120 seconds; preserve raw/staging and exclude candidates from analysis | [Fact model and candidate table](sql/marts/01_fct_survey_responses.sql) |
| Quality | Eleven SQL checks, with errors blocking new findings and warnings kept visible | [Quality checks](sql/tests/) |
| Report | Generate findings, charts and table lineage from the warehouse | [Report](pipeline/report.py), [lineage](reports/lineage.md) |

The duplicate rule is a heuristic, not proof of identity. It compares identical retained answers, excluding timestamp, to the previous identical submission. Review its suitability before using it on a different dataset.

## Run and verify

Python 3.12 is used by CI and the Docker image. Install dependencies in a virtual environment:

```bash
python -m venv .venv
# Linux/macOS; on Windows use .venv\Scripts\Activate.ps1
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m pipeline.run --source sample
```

Running the sample again should insert **zero new raw rows**. Reports are rebuilt only after error-level checks pass. Existing reports from an earlier run are not deleted when a later run fails; check the exit status and quality report before using them.

With Docker:

```bash
docker build -t safetrade .
docker run --rm -v "$(pwd)/reports:/app/reports" safetrade
docker run --rm safetrade python -m pytest -q
```

The [CI workflow](.github/workflows/ci.yml) installs dependencies, checks local README links, runs tests and executes the public sample twice to check repeatability. It uses no live-sheet credentials, does not publish reports and does not deploy the prototype. A successful hosted run is separate evidence from this workflow definition.

## Read more

| Document | Purpose |
|---|---|
| [Findings and decision](docs/findings-and-decision.md) | Current pause decision, limitations and conditions for revisiting |
| [Generated findings](reports/findings.md) | Current sample results with counts and denominators |
| [Original proposal](docs/FirstProposal.pdf) | Initial question and validation plan |
| [Historical decision draft (PDF)](docs/final-report/KeyFindings.pdf) | Retained draft, marked for internal review; not an independently verified new run |
| [Earlier validation study (HTML source)](docs/source/validation-study.html) | Survey design and critique; its earlier continuation recommendation is historical |
| [Design](docs/1-design.md) | Tool choices and pipeline principles |
| [Build](docs/2-build.md) | Python and SQL layers |
| [Testing](docs/3-testing.md) | Checks and regression coverage |
| [Runbook](docs/4-runbook.md) | Setup, safe source handling and troubleshooting |
| [Lessons](docs/5-learnings.md) | Mistakes, changes and what I learned |
| [Data dictionary](docs/data-dictionary.md) | Tables and columns |
| [Data engineering concepts](docs/data-engineering-concepts.md) | Plain-language explanations |

## Privacy and limits

The source sheet stays private. Names, phone numbers, email and free-text stories are removed before landing snapshots are written. The public sample retains answer combinations and precise timestamps, so it should not be described as guaranteed anonymous. Restrict access to original responses and assess disclosure risk before sharing additional data.

CI uses only the sample already committed here. It never connects to the live sheet. Do not publish the private sheet to the web to feed this pipeline; use an authorised private CSV export as described in the runbook.

Built by [Tshidiso Molefe](https://github.com/mlftsh030). Python, DuckDB, SQL, pandas, pytest, matplotlib, Docker and Google Apps Script.
