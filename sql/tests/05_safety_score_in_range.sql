-- severity: error
-- description: Safety score is between 1 and 5 when present.
SELECT response_id, safety_score
FROM staging.stg_survey_responses
WHERE safety_score IS NOT NULL AND safety_score NOT BETWEEN 1 AND 5;
