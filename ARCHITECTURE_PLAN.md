# Nomz Architecture Plan (Current + Updated Composite Scoring)

## 1. Deployment and Runtime
- Platform: AWS Elastic Beanstalk (Python 3.12)
- App: Django monolith (`nomz` app + `restaurants` project)
- DB strategy:
  - Local/dev: SQLite
  - Hosted/prod: PostgreSQL (RDS)
- Static/media: S3-backed in hosted environments

## 2. Data Ingestion Architecture

### Current approach
- Data source adapters under `nomz/ingestion/sources/`
- Normalization and matching under `nomz/ingestion/utils/`
- Persistence and model upserts in `nomz/ingestion/persistence.py`
- Trigger path:
  - Manual command: `python manage.py fetch_nyc_sources`
  - Optional scheduled trigger can be added later (EventBridge + Lambda/cron-like worker)

### Recommended low-cost scheduled setup (when enabled)
- EventBridge scheduled rule (daily or weekly)
- Lambda invokes ingestion command logic
- Writes directly into PostgreSQL
- CloudWatch logs + alarm on failed runs

## 3. Data Model for NYC Restaurant Intelligence

### Core entities
- `Restaurant`
  - canonical restaurant record for UI/search/map
  - stores `composite_score`, `grade_latest`, `grade_score_latest`
- `RestaurantSourceRecord`
  - provenance records for EATERIES, DINING_OUT, DOHMH
- `InspectionRecord`
  - inspection outcomes and violations
- `DiningOutLocation`
  - permit/license/location metadata
- `DataIngestionRun`
  - ingestion run tracking and error log

### User review entities (updated)
- `Review`
  - `rating` (overall, 1-5)
  - `food_quality_rating` (1-5)
  - `service_quality_rating` (1-5)
  - `ambience_rating` (1-5)
  - `location_rating` (1-5)
  - `value_rating` (1-5)
  - `dietary_accommodation_rating` (1-5)
  - `cleanliness_rating` (1-5)
  - moderation controls: `is_flagged`, `is_deleted`
- `ModerationReport`
  - user reporting and admin moderation flow

## 4. Record Linking / Merge Strategy
- Primary matching keys:
  - normalized name
  - street/building
  - ZIP prefix
  - borough fallback
- Matching utility:
  - resolver-based confidence matching
  - if no strong match: create new restaurant record
- Source lineage always retained in `RestaurantSourceRecord`

## 5. Composite Score v2 (Review-Dominant)

## Goal
Make user experience signals the most significant input while preserving hygiene/compliance signals from inspections.

### 5.1 Component scores
- **User Experience Signal** (0-100)
  - Built from multi-parameter review ratings
  - Weighted inside review signal:
    - Food: 27%
    - Service: 20%
    - Ambience: 14%
    - Location: 10%
    - Value: 12%
    - Dietary accommodation: 7%
    - Cleanliness: 6%
    - Overall rating: 4%
  - Includes:
    - Bayesian smoothing for low review count
    - Review recency weighting
    - Confidence metric by volume

- **Inspection & Hygiene Signal** (0-100)
  - Combines latest inspection:
    - Grade score
    - Violation severity (critical heavier than non-critical)
    - Inspection recency

- **Price-to-Value Fit** (0-100)
  - Uses value ratings adjusted against expected value at the restaurant’s price tier

- **Operational Reliability** (0-100)
  - Uses active/unavailable/flag status
  - Includes completeness/reliability metadata (hours, coordinates, permit status when available)

### 5.2 Final weighted formula

When at least one non-deleted, non-flagged review exists:

`Composite = 0.65*UserExperience + 0.20*Inspection + 0.10*PriceValue + 0.05*Operations`

Cold-start fallback (no reviews):

`Composite = 0.30*UserExperienceNeutral + 0.45*Inspection + 0.10*PriceValue + 0.15*Operations`

### 5.3 Why this design
- Satisfies requirement that reviews are the dominant signal
- Prevents score volatility with very small review counts
- Still preserves health/safety compliance relevance

## 6. Recalculation Triggers
- During ingestion updates (inspection updates)
- On review submission
- On moderation actions that flag/unflag/delete review content
- Owner dashboard reads factor breakdown and trend view from the same scoring engine

## 7. User Review Module Changes
- Review form now requires multi-parameter scoring, not just a single star rating
- Review details pages display sub-ratings to support transparency
- Admin moderation keeps the same flow and now correctly re-syncs composite score after actions

## 8. Owner Analytics Surfaces
- Composite score summary
- Factor breakdown table
- Neighborhood comparison
- Historical trend data points
- Review confidence and per-factor averages

## 9. Future Extensions
- NLP sentiment scoring from free-text comments
- Time-windowed trend lines (30/90/180 day)
- Neighborhood percentile benchmarks by cuisine + price tier
- Fraud detection weighting for suspicious review clusters
