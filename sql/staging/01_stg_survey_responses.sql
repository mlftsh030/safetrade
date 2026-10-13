-- STAGING: one clean row per response.
-- Rules for this layer: rename, trim, fix types, and map free text to a
-- small fixed set of categories. No joins, no totals.
-- Matching uses patterns (e.g. 'no, never%') instead of exact text, so
-- 'No, never' and 'No, Never' land in the same category.

CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_survey_responses AS
WITH src AS (
    SELECT
        response_id,
        try_cast("timestamp" AS TIMESTAMPTZ)                AS submitted_at,
        nullif(trim(age), '')                               AS age_band,
        nullif(lower(trim(frequency)), '')                  AS marketplace_frequency,
        lower(trim(bought_online))                          AS bought_online_txt,
        lower(trim(safety_feeling))                         AS safety_txt,
        lower(trim(scam_experience))                        AS scam_txt,
        nullif(trim(top_concerns), '')                      AS top_concerns_raw,
        lower(trim(stopped_using))                          AS stop_txt,
        lower(trim(cancelled_deal))                         AS cancel_txt,
        nullif(trim(wanted_features), '')                   AS wanted_features_raw,
        lower(trim(price_willing))                          AS price_txt,
        lower(trim(when_pay))                               AS pay_txt,
        _batch_id,
        _loaded_at
    FROM raw.survey_responses
)
SELECT
    response_id,
    submitted_at,
    age_band,
    marketplace_frequency,

    -- "How often do you use Facebook Marketplace?" Anyone who does not
    -- answer 'never' is a Marketplace user: the people the survey targets.
    marketplace_frequency <> 'never'                    AS is_marketplace_user,

    -- "Have you ever bought or sold something online?" (any site, not only Marketplace)
    CASE bought_online_txt WHEN 'yes' THEN true WHEN 'no' THEN false END
        AS has_bought_or_sold_online,

    -- How safe people feel, as a category and as a 1-5 score.
    CASE
        WHEN safety_txt IS NULL OR safety_txt = '' THEN NULL
        WHEN safety_txt = 'very unsafe' THEN 'very_unsafe'
        WHEN safety_txt = 'unsafe'      THEN 'unsafe'
        WHEN safety_txt = 'neutral'     THEN 'neutral'
        WHEN safety_txt = 'safe'        THEN 'safe'
        WHEN safety_txt = 'very safe'   THEN 'very_safe'
        ELSE 'unmapped'
    END AS safety_feeling,
    CASE safety_txt
        WHEN 'very unsafe' THEN 1 WHEN 'unsafe' THEN 2 WHEN 'neutral' THEN 3
        WHEN 'safe' THEN 4 WHEN 'very safe' THEN 5
    END AS safety_score,

    -- Scam experience. The first notebook missed 'Yes — it happened to me'
    -- and 'No, Never'. Pattern matching catches both.
    CASE
        WHEN scam_txt IS NULL OR scam_txt = '' THEN NULL
        WHEN scam_txt LIKE 'yes%'      THEN 'scammed'
        WHEN scam_txt LIKE 'almost%'   THEN 'almost_scammed'
        WHEN scam_txt LIKE 'no, but%'  THEN 'worried_not_scammed'
        WHEN scam_txt LIKE 'no, never%' THEN 'never_scammed'
        ELSE 'unmapped'
    END AS scam_experience,

    top_concerns_raw,

    CASE
        WHEN stop_txt IS NULL OR stop_txt = '' THEN NULL
        WHEN stop_txt LIKE 'very likely%' THEN 'very_likely'
        WHEN stop_txt LIKE 'likely%'      THEN 'likely'
        WHEN stop_txt LIKE 'not likely%'  THEN 'not_likely'
        ELSE 'unmapped'
    END AS likelihood_to_stop_using,

    CASE
        WHEN cancel_txt IS NULL OR cancel_txt = '' THEN NULL
        WHEN cancel_txt LIKE 'yes%more than once%' THEN 'more_than_once'
        WHEN cancel_txt LIKE 'yes%once%'           THEN 'once'
        WHEN cancel_txt LIKE 'no, but%'            THEN 'considered'
        WHEN cancel_txt = 'no'                     THEN 'never'
        ELSE 'unmapped'
    END AS cancelled_deal,

    wanted_features_raw,

    -- Fee people would pay. The first notebook put 'R10 – R20' into 'low'
    -- because the text contains 'r10'. Here it has its own band.
    CASE
        WHEN price_txt IS NULL OR price_txt = '' THEN NULL
        WHEN price_txt LIKE 'r0%'                  THEN 'none'
        WHEN contains(price_txt, '%')              THEN 'percentage'
        WHEN regexp_matches(price_txt, '^r5\s*[–-]\s*r10')  THEN 'r5_to_r10'
        WHEN regexp_matches(price_txt, '^r10\s*[–-]\s*r20') THEN 'r10_to_r20'
        WHEN price_txt LIKE 'r20+%'                THEN 'r20_plus'
        ELSE 'unmapped'
    END AS fee_willingness,

    -- A rough rand value for fixed-fee answers, so bands can be compared.
    -- Midpoint of each band; 'R20+' uses its minimum. Percentages stay NULL
    -- because they depend on the item price.
    CASE
        WHEN price_txt LIKE 'r0%' THEN 0
        WHEN regexp_matches(price_txt, '^r5\s*[–-]\s*r10')  THEN 7.5
        WHEN regexp_matches(price_txt, '^r10\s*[–-]\s*r20') THEN 15
        WHEN price_txt LIKE 'r20+%' THEN 20
    END AS fee_estimate_rand,

    CASE
        WHEN pay_txt IS NULL OR pay_txt = '' THEN NULL
        WHEN pay_txt LIKE 'after%'               THEN 'after'
        WHEN pay_txt LIKE 'before%'              THEN 'before'
        WHEN pay_txt LIKE 'only for high-value%' THEN 'high_value_only'
        ELSE 'unmapped'
    END AS payment_timing,

    _batch_id,
    _loaded_at
FROM src;
