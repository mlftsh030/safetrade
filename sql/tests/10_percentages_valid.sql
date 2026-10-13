-- severity: error
-- description: Every percentage in the marts is between 0 and 1.
SELECT 'headline' AS mart, segment || ':' || metric AS item, pct FROM marts.mart_headline_metrics WHERE pct NOT BETWEEN 0 AND 1
UNION ALL SELECT 'concerns', concern, pct_of_answered FROM marts.mart_concerns WHERE pct_of_answered NOT BETWEEN 0 AND 1
UNION ALL SELECT 'features', feature, pct_of_answered FROM marts.mart_features WHERE pct_of_answered NOT BETWEEN 0 AND 1;
