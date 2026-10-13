-- severity: error
-- description: Every response has a submission time that is not in the future.
SELECT response_id, submitted_at
FROM staging.stg_survey_responses
WHERE submitted_at IS NULL OR submitted_at > now();
