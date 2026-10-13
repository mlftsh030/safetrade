-- severity: warn
-- description: People who never use Facebook Marketplace but answered the Marketplace scam question. They are not the target users, so results are also shown for Marketplace users only.
SELECT response_id, marketplace_frequency, scam_experience
FROM staging.stg_survey_responses
WHERE marketplace_frequency = 'never' AND scam_experience IS NOT NULL;
