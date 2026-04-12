# Composite Scoring Logic (Audit Guide)

This document describes how Nomz computes and audits restaurant composite scores.

## Algorithm version
- Current version: `v2`
- Source of truth: `nomz/ingestion/utils/score.py` and `nomz/scoring.py`

## Scoring factors
The composite score is normalized to `0..100` and combines:
- `User Experience Signal` (review-derived, confidence-weighted)
- `Inspection & Hygiene` (grade, violation, and recency components)
- `Price-to-Value Fit`
- `Operational Reliability`

The exact weights are dynamic and depend on available data:
- With reviews: review-heavy weighting
- No reviews + inspections: inspection-heavy weighting
- No reviews + no inspections: operational fallback weighting

## Recalculation entry points
Scores are recomputed when:
- Reviews are created/deleted (signals)
- Inspection records are created/deleted (signals)
- Admin triggers recomputation from dashboard
- Django admin bulk action triggers recomputation
- `recalculate_composite_scores` command runs
- Ingestion pipeline refreshes matched restaurants

## Historical records
Every recomputation writes a `CompositeScoreHistory` row with:
- trigger source and actor
- previous score, new score, delta
- breakdown and raw inputs used by the algorithm
- anomaly flags (if detected)

This enables transparent traceability for ranking changes over time.

## Anomaly detection
Anomalies are stored as `CompositeScoreAnomaly` rows and currently include:
- Large one-step score deltas (>=20 points)
- High score with low review confidence
- High score with stale inspection data

Open anomalies are shown on the admin dashboard and can be marked resolved.

## Verification workflow
To validate accuracy with sample data:
1. Seed/ingest representative restaurants, inspections, and reviews.
2. Run `python manage.py recalculate_composite_scores`.
3. Inspect `CompositeScoreHistory` and `CompositeScoreAnomaly` records in admin.
4. Compare output fields (`score_breakdown`, `score_inputs`) against expected inputs.
