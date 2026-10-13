-- INTERMEDIATE: one row per (response, wanted feature). Same idea as concerns.

CREATE SCHEMA IF NOT EXISTS intermediate;

CREATE OR REPLACE TABLE intermediate.int_response_features AS
WITH split AS (
    SELECT
        response_id,
        trim(unnest(string_split(wanted_features_raw, ','))) AS feature_label
    FROM staging.stg_survey_responses
    WHERE wanted_features_raw IS NOT NULL
)
SELECT DISTINCT
    response_id,
    feature_label,
    CASE
        WHEN lower(feature_label) LIKE '%escrow%'          THEN 'escrow'
        WHEN lower(feature_label) LIKE 'verified user%'    THEN 'verified_profiles'
        WHEN lower(feature_label) LIKE 'id verification%'  THEN 'id_verification'
        WHEN lower(feature_label) LIKE 'ratings%'          THEN 'ratings_and_reviews'
        WHEN lower(feature_label) LIKE 'safe meetup%'      THEN 'safe_meetup_locations'
        ELSE 'other'
    END AS feature
FROM split
WHERE feature_label <> '';
