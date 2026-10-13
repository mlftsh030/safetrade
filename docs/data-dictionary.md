# Data dictionary

**Every table the pipeline builds, and what each column means.**

## raw.survey_responses

Exactly what was received, all text, personal data already removed.

| Column | Survey question |
|---|---|
| response_id | Built by the pipeline: hash of the answers |
| timestamp | When the response was submitted |
| age | What's your age group? |
| frequency | How often do you use Facebook Marketplace? |
| bought_online | Have you ever bought or sold something online? |
| safety_feeling | How safe do you feel using Facebook Marketplace? |
| scam_experience | Have you ever experienced or nearly experienced a scam on Marketplace? |
| top_concerns | What concerns you most about Marketplace? (multi-choice) |
| stopped_using | How likely are you to stop using Marketplace because of safety concerns? |
| cancelled_deal | Have you ever cancelled a deal because you felt unsafe? |
| wanted_features | What features would make you feel safer? (multi-choice) |
| price_willing | How much would you pay per transaction for guaranteed safety? |
| when_pay | When would you prefer to pay the safety fee? |
| _batch_id, _loaded_at, _source | Which run loaded the row, when, and from which file |

## raw.load_log

One row per run: `batch_id`, `source_file`, `rows_in_file`, `rows_inserted`, `loaded_at`.

## staging.stg_survey_responses

One clean row per response.

| Column | Type | Values |
|---|---|---|
| submitted_at | timestamp | |
| is_double_submission | boolean | true if identical answers arrived in the 2 minutes before; left out of intermediate and marts |
| age_band | text | 18–24, 25–34 |
| marketplace_frequency | text | never, occasionally, weekly, daily |
| is_marketplace_user | boolean | true unless frequency is "never" |
| has_bought_or_sold_online | boolean | |
| safety_feeling | text | very_unsafe, unsafe, neutral, safe, very_safe |
| safety_score | integer | 1 (very unsafe) to 5 (very safe) |
| scam_experience | text | scammed, almost_scammed, worried_not_scammed, never_scammed |
| likelihood_to_stop_using | text | very_likely, likely, not_likely |
| cancelled_deal | text | more_than_once, once, considered, never |
| fee_willingness | text | none, r5_to_r10, r10_to_r20, r20_plus, percentage |
| fee_estimate_rand | number | 0, 7.5, 15, 20 (band midpoint; R20+ uses its minimum); empty for percentage |
| payment_timing | text | after, before, high_value_only |
| top_concerns_raw, wanted_features_raw | text | the original multi-choice cells |

Any answer that doesn't match a rule becomes `unmapped`, which fails quality check 04.

## intermediate.int_response_concerns / int_response_features

One row per (response, choice). Columns: `response_id`, the original label, and a code:

- concerns: fake_sellers, payment_fraud, product_not_as_described, meeting_strangers, no_recourse
- features: escrow, verified_profiles, id_verification, ratings_and_reviews, safe_meetup_locations

## marts.fct_survey_responses

One row per response (double submissions left out): every staging column, plus

| Column | Meaning |
|---|---|
| segment | marketplace_users or non_users |
| feels_unsafe | safety_feeling is unsafe or very_unsafe |
| scammed_or_nearly | scam_experience is scammed or almost_scammed |
| has_cancelled_deal | cancelled once or more than once |
| willing_to_pay_fee | fee_willingness is anything except none |
| concern_* | 1 if that concern was ticked, 0 if not, empty if the question was skipped |
| wants_* | same, for wanted features |

## marts.mart_question_breakdown

One row per (question, answer): `respondents`, `answered`, `total_responses`, `pct_of_answered`.

## marts.mart_concerns / mart_features

One row per option: `respondents`, `answered`, `pct_of_answered`.

## marts.mart_headline_metrics

One row per (segment, metric): `label`, `numerator`, `denominator`, `pct`. Segments: all, marketplace_users, non_users.

## marts.mart_validation_scorecard

One row per proposal success criterion: `value_marketplace_users`, `n_marketplace_users`, `value_all_respondents`, `threshold`, `status` (met, not_met, not_measured_yet).
