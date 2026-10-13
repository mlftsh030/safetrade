-- severity: error
-- description: Staging has the same number of rows as raw (nothing dropped or doubled).
SELECT (SELECT count(*) FROM raw.survey_responses) AS raw_rows,
       (SELECT count(*) FROM staging.stg_survey_responses) AS staging_rows
WHERE raw_rows <> staging_rows;
