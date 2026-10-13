-- severity: error
-- description: Every response appears once in raw (no duplicates from re-runs).
SELECT response_id, count(*) AS copies
FROM raw.survey_responses
GROUP BY response_id
HAVING count(*) > 1;
