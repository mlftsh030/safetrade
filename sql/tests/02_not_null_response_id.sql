-- severity: error
-- description: Every response has an ID.
SELECT * FROM raw.survey_responses WHERE response_id IS NULL OR response_id = '';
