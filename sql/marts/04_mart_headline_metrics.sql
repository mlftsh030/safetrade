-- MART: the key numbers, each with its numerator and denominator, so anyone
-- can check how it was worked out. Calculated three times:
--   all                -> everyone who answered
--   marketplace_users  -> people who use Facebook Marketplace (the target users)
--   non_users          -> people who never use it
-- Splitting by segment matters: 56% of respondents never use Marketplace,
-- and the two groups answer very differently.

CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.mart_headline_metrics AS
WITH f AS (
    SELECT *, 'all' AS seg FROM marts.fct_survey_responses
    UNION ALL
    SELECT *, segment AS seg FROM marts.fct_survey_responses
),
m AS (
    SELECT seg, 1 AS sort_order, 'feel_unsafe' AS metric,
           'Feel unsafe or very unsafe using Marketplace' AS label,
           count(*) FILTER (feels_unsafe) AS numerator,
           count(safety_feeling) AS denominator FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 2, 'scammed_or_nearly', 'Were scammed, or nearly scammed, on Marketplace',
           count(*) FILTER (scammed_or_nearly), count(scam_experience) FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 3, 'cancelled_deal', 'Have cancelled a deal because they felt unsafe',
           count(*) FILTER (has_cancelled_deal), count(cancelled_deal) FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 4, 'likely_to_stop', 'Likely to stop using Marketplace over safety',
           count(*) FILTER (likelihood_to_stop_using IN ('likely', 'very_likely')),
           count(likelihood_to_stop_using) FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 5, 'want_escrow', 'Want money held safely until the item arrives (escrow)',
           count(*) FILTER (wants_escrow = 1), count(wants_escrow) FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 6, 'willing_to_pay', 'Willing to pay some fee for a safer transaction',
           count(*) FILTER (willing_to_pay_fee), count(fee_willingness) FROM f GROUP BY seg
    UNION ALL
    SELECT seg, 7, 'pay_after', 'Prefer to pay the safety fee after the deal',
           count(*) FILTER (payment_timing = 'after'), count(payment_timing) FROM f GROUP BY seg
)
SELECT
    seg AS segment, sort_order, metric, label, numerator, denominator,
    round(numerator / nullif(denominator, 0), 4) AS pct
FROM m
ORDER BY CASE seg WHEN 'all' THEN 0 WHEN 'marketplace_users' THEN 1 ELSE 2 END, sort_order;
