"""Settings shared by every step of the pipeline.

Keeping paths and rules in one place means a change (a new PII column,
a new folder) is made once, not in five files.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SAMPLE_SOURCE = ROOT / "data" / "sample" / "survey_responses_sample.csv"
LANDING_DIR = ROOT / "data" / "landing"          # raw snapshots, one per run
WAREHOUSE_PATH = ROOT / "data" / "warehouse" / "safetrade.duckdb"
SQL_DIR = ROOT / "sql"
REPORTS_DIR = ROOT / "reports"

# The private Google Sheet export link is read from this environment
# variable so it never appears in the code or in Git.
SHEET_URL_ENV = "SAFETRADE_SHEET_URL"

# Columns that identify a person. They are removed during extract,
# BEFORE anything is saved, so personal data never reaches the warehouse.
PII_COLUMNS = {"name", "phone", "email", "scam_story", "trust_insight"}

# The survey questions the pipeline expects after PII is removed.
EXPECTED_COLUMNS = [
    "timestamp",
    "age",
    "frequency",
    "bought_online",
    "safety_feeling",
    "scam_experience",
    "top_concerns",
    "stopped_using",
    "cancelled_deal",
    "wanted_features",
    "price_willing",
    "when_pay",
]

# The raw sheet had a spelling mistake in one header. We fix it here,
# so every later step can use the correct name.
HEADER_FIXES = {"stoped_using": "stopped_using"}

# Order the SQL layers run in. Each layer only reads from the one before.
TRANSFORM_LAYERS = ["staging", "intermediate", "marts"]

# Proposal success criterion 2 says a "meaningful portion" must be willing
# to pay. The proposal gave no number, so this is our stated assumption.
WILLING_TO_PAY_THRESHOLD = 0.5
