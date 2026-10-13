-- MART: the main analysis table. One row per response, every answer as a
-- clean column, plus a 0/1 flag for each concern and wanted feature.
-- This is the table an analyst or a BI tool (Power BI, Tableau) connects to.

CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.fct_survey_responses AS
WITH concern_flags AS (
    SELECT
        response_id,
        max((concern = 'fake_sellers')::INT)             AS concern_fake_sellers,
        max((concern = 'payment_fraud')::INT)            AS concern_payment_fraud,
        max((concern = 'product_not_as_described')::INT) AS concern_product_not_as_described,
        max((concern = 'meeting_strangers')::INT)        AS concern_meeting_strangers,
        max((concern = 'no_recourse')::INT)              AS concern_no_recourse
    FROM intermediate.int_response_concerns
    GROUP BY response_id
),
feature_flags AS (
    SELECT
        response_id,
        max((feature = 'escrow')::INT)                AS wants_escrow,
        max((feature = 'verified_profiles')::INT)     AS wants_verified_profiles,
        max((feature = 'id_verification')::INT)       AS wants_id_verification,
        max((feature = 'ratings_and_reviews')::INT)   AS wants_ratings_and_reviews,
        max((feature = 'safe_meetup_locations')::INT) AS wants_safe_meetup_locations
    FROM intermediate.int_response_features
    GROUP BY response_id
)
SELECT
    s.response_id,
    s.submitted_at,
    s.age_band,
    s.marketplace_frequency,
    s.is_marketplace_user,
    CASE WHEN s.is_marketplace_user THEN 'marketplace_users' ELSE 'non_users' END AS segment,
    s.has_bought_or_sold_online,
    s.safety_feeling,
    s.safety_score,
    s.safety_feeling IN ('unsafe', 'very_unsafe')        AS feels_unsafe,
    s.scam_experience,
    s.scam_experience IN ('scammed', 'almost_scammed')   AS scammed_or_nearly,
    s.likelihood_to_stop_using,
    s.cancelled_deal,
    s.cancelled_deal IN ('once', 'more_than_once')       AS has_cancelled_deal,
    s.fee_willingness,
    s.fee_willingness <> 'none'                          AS willing_to_pay_fee,
    s.fee_estimate_rand,
    s.payment_timing,
    c.* EXCLUDE (response_id),
    f.* EXCLUDE (response_id)
FROM staging.stg_survey_responses s
LEFT JOIN concern_flags c USING (response_id)
LEFT JOIN feature_flags f USING (response_id);
