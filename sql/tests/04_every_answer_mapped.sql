-- severity: error
-- description: Every single-choice answer maps to a known category (no 'unmapped'). This check would have caught the two bugs in the first notebook.
SELECT question, answer, respondents
FROM marts.mart_question_breakdown
WHERE answer = 'unmapped';
