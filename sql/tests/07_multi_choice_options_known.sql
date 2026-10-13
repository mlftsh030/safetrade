-- severity: warn
-- description: Every ticked concern or feature is a known option. A new option in the survey shows up here as 'other'.
SELECT 'concern' AS kind, concern_label AS label, count(*) AS n
FROM intermediate.int_response_concerns WHERE concern = 'other' GROUP BY ALL
UNION ALL
SELECT 'feature', feature_label, count(*)
FROM intermediate.int_response_features WHERE feature = 'other' GROUP BY ALL;
