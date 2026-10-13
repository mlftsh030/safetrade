-- INTERMEDIATE: one row per (response, concern).
-- People could tick several concerns, saved as one comma-separated cell.
-- Splitting it into rows ("unnesting") makes counting simple and means a
-- new option shows up automatically, instead of needing a new column.

CREATE SCHEMA IF NOT EXISTS intermediate;

CREATE OR REPLACE TABLE intermediate.int_response_concerns AS
WITH split AS (
    SELECT
        response_id,
        trim(unnest(string_split(top_concerns_raw, ','))) AS concern_label
    FROM staging.stg_survey_responses
    WHERE top_concerns_raw IS NOT NULL
)
SELECT DISTINCT
    response_id,
    concern_label,
    CASE
        WHEN lower(concern_label) LIKE 'fake sellers%'      THEN 'fake_sellers'
        WHEN lower(concern_label) LIKE 'payment fraud%'     THEN 'payment_fraud'
        WHEN lower(concern_label) LIKE 'product not as%'    THEN 'product_not_as_described'
        WHEN lower(concern_label) LIKE 'meeting strangers%' THEN 'meeting_strangers'
        WHEN lower(concern_label) LIKE 'no recourse%'       THEN 'no_recourse'
        ELSE 'other'
    END AS concern
FROM split
WHERE concern_label <> '';
