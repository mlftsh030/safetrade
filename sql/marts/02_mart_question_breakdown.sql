-- MART: how people answered each single-choice question.
-- Long format: one row per (question, answer). Percentages use the people
-- who ANSWERED that question, not everyone, so a skipped question does not
-- pull the number down. The denominator is stored next to every number.

CREATE SCHEMA IF NOT EXISTS marts;

CREATE OR REPLACE TABLE marts.mart_question_breakdown AS
WITH long AS (
    SELECT 'safety_feeling'           AS question, safety_feeling           AS answer FROM marts.fct_survey_responses
    UNION ALL SELECT 'scam_experience',            scam_experience          FROM marts.fct_survey_responses
    UNION ALL SELECT 'likelihood_to_stop_using',   likelihood_to_stop_using FROM marts.fct_survey_responses
    UNION ALL SELECT 'cancelled_deal',             cancelled_deal           FROM marts.fct_survey_responses
    UNION ALL SELECT 'fee_willingness',            fee_willingness          FROM marts.fct_survey_responses
    UNION ALL SELECT 'payment_timing',             payment_timing           FROM marts.fct_survey_responses
    UNION ALL SELECT 'age_band',                   age_band                 FROM marts.fct_survey_responses
),
answered AS (
    SELECT question, count(answer) AS answered, count(*) AS total_responses
    FROM long GROUP BY question
)
SELECT
    l.question,
    l.answer,
    count(*)                              AS respondents,
    a.answered,
    a.total_responses,
    round(count(*) / a.answered, 4)       AS pct_of_answered
FROM long l
JOIN answered a USING (question)
WHERE l.answer IS NOT NULL
GROUP BY l.question, l.answer, a.answered, a.total_responses
ORDER BY l.question, respondents DESC;
