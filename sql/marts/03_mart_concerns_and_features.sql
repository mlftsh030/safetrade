-- MART: how often each concern and each wanted feature was ticked.
-- Denominator: people who answered that multi-choice question.

CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.mart_concerns AS
WITH answered AS (
    SELECT count(DISTINCT response_id) AS n FROM intermediate.int_response_concerns
)
SELECT
    concern,
    any_value(concern_label)                         AS example_label,
    count(DISTINCT response_id)                      AS respondents,
    (SELECT n FROM answered)                         AS answered,
    round(count(DISTINCT response_id) / (SELECT n FROM answered), 4) AS pct_of_answered
FROM intermediate.int_response_concerns
GROUP BY concern
ORDER BY respondents DESC;

CREATE OR REPLACE TABLE marts.mart_features AS
WITH answered AS (
    SELECT count(DISTINCT response_id) AS n FROM intermediate.int_response_features
)
SELECT
    feature,
    any_value(feature_label)                         AS example_label,
    count(DISTINCT response_id)                      AS respondents,
    (SELECT n FROM answered)                         AS answered,
    round(count(DISTINCT response_id) / (SELECT n FROM answered), 4) AS pct_of_answered
FROM intermediate.int_response_features
GROUP BY feature
ORDER BY respondents DESC;
