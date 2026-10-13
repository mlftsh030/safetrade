-- MART: the proposal's success criteria (section 6.4), scored from data.
-- This is where the pipeline answers the business question:
-- proceed, refine, or reassess?
-- The status is judged on Marketplace users, because the proposal targets
-- them. The all-respondent value is shown next to it for comparison.

CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.mart_validation_scorecard AS
WITH h AS (SELECT segment, metric, pct, denominator FROM marts.mart_headline_metrics),
criteria AS (
    SELECT 1 AS criterion_no,
           'A majority are concerned about transaction safety' AS criterion,
           'feel_unsafe' AS metric,
           0.5 AS threshold
    UNION ALL
    SELECT 2,
           'A meaningful portion are willing to pay (threshold is our assumption)',
           'willing_to_pay',
           getvariable('willing_to_pay_threshold')
    UNION ALL
    SELECT 3,
           'Observable interest in a "Pay securely" option (clicks, sign-ups)',
           NULL,
           NULL
)
SELECT
    c.criterion_no,
    c.criterion,
    u.pct          AS value_marketplace_users,
    u.denominator  AS n_marketplace_users,
    a.pct          AS value_all_respondents,
    c.threshold,
    CASE
        WHEN c.metric IS NULL THEN 'not_measured_yet'
        WHEN u.pct > c.threshold THEN 'met'
        ELSE 'not_met'
    END AS status
FROM criteria c
LEFT JOIN h u ON u.metric = c.metric AND u.segment = 'marketplace_users'
LEFT JOIN h a ON a.metric = c.metric AND a.segment = 'all'
ORDER BY c.criterion_no;
