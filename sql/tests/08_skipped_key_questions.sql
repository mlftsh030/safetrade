-- severity: warn
-- description: Responses that skipped a key question. Not an error (questions were optional), but worth knowing.
SELECT response_id,
       safety_feeling IS NULL AS skipped_safety,
       scam_experience IS NULL AS skipped_scam,
       fee_willingness IS NULL AS skipped_fee
FROM staging.stg_survey_responses
WHERE safety_feeling IS NULL OR scam_experience IS NULL OR fee_willingness IS NULL;
