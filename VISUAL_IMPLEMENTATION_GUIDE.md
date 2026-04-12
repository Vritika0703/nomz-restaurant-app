# Visual Implementation Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RECOMMENDATION SYSTEM FLOW                        │
└─────────────────────────────────────────────────────────────────────┘

1. INITIAL RECOMMENDATION PHASE
═════════════════════════════════════════════════════════════════════

  User with Preferences                Restaurant Catalog
         │                                     │
         └──────────────┬──────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────┐
        │   recommend_restaurants_for_user() │
        │   (with learning enabled)          │
        └────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    Base Score    Historical        Time-Weighted
    (Static)      Satisfaction      Interactions
    - Cuisine     (Learned)         (Recent = 2x)
    - Price       - Past reviews
    - Dietary     - Similar cuisine
    - Location    - Pattern analysis

        └───────────────┬───────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │   Apply Learned Weights        │
        │  cuisine_weight=1.2            │
        │  dietary_weight=0.9            │
        │  price_weight=1.1              │
        │  neighborhood_weight=0.8       │
        │  quality_weight=1.3            │
        └────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │   Final Ranked List            │
        │   1. Restaurant A (score:8.5)  │
        │   2. Restaurant B (score:7.9)  │
        │   3. Restaurant C (score:7.2)  │
        │   4. Restaurant D (score:6.8)  │
        └────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────┐
        │ RecalculatedRecommendation     │
        │ Records Created (for tracking) │
        └────────────────────────────────┘
                        │
                    (Sent to user)


2. USER INTERACTION PHASE
═════════════════════════════════════════════════════════════════════

  User clicks on recommendation
         │
         ▼
  Logs: UserInteractionHistory
   - Type: "recommendation_clicked"
   - Restaurant: A
   - Rank: 1
   - Time: now
         │
         ▼
  User reads reviews, views menu
         │
         ▼
  Logs: UserInteractionHistory
   - Type: "profile_view"
   - Time spent: 180 seconds
         │
         ▼
  User writes review & rates 4.5/5
         │
         ▼
  Signal triggered: post_save(Review)


3. LEARNING PHASE
═════════════════════════════════════════════════════════════════════

  [Signal Handler Triggered]
           │
           ▼
  ┌─────────────────────────────────┐
  │ Create UserInteractionHistory   │
  │ - Type: "review_submitted"      │
  │ - Satisfaction: 4.5/5           │
  └─────────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────┐
  │ Update RecalculatedRecommendation│
  │ - user_interacted = True        │
  │ - days_to_interaction = 2       │
  │ - accuracy_feedback = 1 (good)  │
  └─────────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────┐
  │ recalculate_user_recommendation │
  │_model(user_id)                  │
  │                                 │
  │ Analyze interactions:           │
  │ - Recent cuisine matches: 100%  │
  │   success rate                  │
  │ - Price matches: 80% success    │
  │ - Dietary matches: 60% success  │
  └─────────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────┐
  │ Adjust UserPreference Weights   │
  │                                 │
  │ Before:                         │
  │  cuisine_weight = 1.0           │
  │  price_weight = 1.0             │
  │                                 │
  │ After:                          │
  │  cuisine_weight = 1.05 (+)      │
  │  price_weight = 0.96 (-)        │
  │                                 │
  │ recommendation_model_version: 2 │
  └─────────────────────────────────┘
           │
           ▼
  ┌─────────────────────────────────┐
  │ Update RecommendationModelMetric│
  │ - total_recommendations: 100    │
  │ - successful: 85 (85% accuracy) │
  │ - avg_days_to_interaction: 1.8  │
  └─────────────────────────────────┘


4. IMPROVED RECOMMENDATIONS (Next Cycle)
═════════════════════════════════════════════════════════════════════

  User gets new recommendations
         │
         ▼
  recommend_restaurants_for_user()
  (with NEW learned weights)
         │
         ▼
  Cuisine matches weighted 1.05x (increased)
  Price matches weighted 0.96x (decreased)
         │
         ▼
  Similar restaurants to one user rated
  4.5/5 now score higher (→ +2 boost)
         │
         ▼
  IMPROVED recommendations displayed
  (better match to user preferences)


5. BATCH DAILY RECALCULATION (Optional)
═════════════════════════════════════════════════════════════════════

  [Daily 2:00 AM - Cron Job]
         │
         ▼
  python manage.py recalculate_recommendations
         │
         ├── For each user with preferences:
         │   ├─ Analyze last 90 days interactions
         │   ├─ Calculate success rates
         │   ├─ Adjust weights
         │   └─ Update model version
         │
         └── Calculate daily metrics:
             ├─ avg_recommendation_accuracy
             ├─ avg_days_to_interaction
             ├─ cuisine_match_success_rate
             └─ RecommendationModelMetric stored
         │
         ▼
  System continuously improves
  (autonomous learning loop)
```

---

## Data Model Relationships

```
┌────────────────────────────────┐
│       Django User              │
│  (from auth.models)            │
│                                │
│  - username                    │
│  - email                       │
│  - date_joined                 │
└────────────┬───────────────────┘
             │ 1:1
             ▼
┌────────────────────────────────┐
│      UserPreference            │
│   (ENHANCED with learning)     │
│                                │
│  ✓ favorite_cuisines           │
│  ✓ dietary_restrictions        │
│  ✓ price_preference            │
│  ✓ neighborhood_preference     │
│                                │
│  🆕 cuisine_weight = 1.2       │
│  🆕 dietary_weight = 0.9       │
│  🆕 price_weight = 1.1         │
│  🆕 neighborhood_weight = 0.8  │
│  🆕 composite_score_weight=1.3 │
│  🆕 historical_sat_weight=0.5  │
│                                │
│  🆕 total_recommendations_recv │
│  🆕 successful_recommendations │
│  🆕 recommendation_model_ver=2 │
│  🆕 last_recommendation_calc   │
│  🆕 learning_data_quality=87%  │
└────────────┬───────────────────┘
             │
             │ 1:N
             ├─────────────────────────────────┐
             │                                 │
             ▼                                 ▼
    ┌──────────────────────┐    ┌────────────────────────────┐
    │  UserInteraction     │    │  RecalculatedRecommendation│
    │  History (NEW)       │    │  (NEW)                     │
    │                      │    │                            │
    │  🆕 interaction_type │    │  🆕 recommendation_score   │
    │  🆕 restaurant_id    │    │  🆕 cuisine_score          │
    │  🆕 satisfaction_    │    │  🆕 price_score            │
    │     score = 4.5      │    │  🆕 accuracy_feedback      │
    │  🆕 time_spent_sec   │    │  🆕 user_interacted = True │
    │  🆕 was_recommended  │    │  🆕 days_to_interaction=2  │
    │  🆕 recommendation_  │    │  🆕 calculated_at          │
    │     rank = 1         │    │                            │
    │  created_at (many)   │    │  (tracks accuracy)         │
    └──────────────────────┘    └────────────────────────────┘
             │                           │
             │ N:1                       │ N:1
             │                           │
             └───────────────┬───────────┘
                             │
                             ▼
            ┌────────────────────────────┐
            │     Restaurant             │
            │                            │
            │  - name                    │
            │  - cuisine_type            │
            │  - price_range             │
            │  - composite_score         │
            │  - neighborhood            │
            │  - is_active, is_flagged   │
            └────────────────────────────┘


                    Daily Aggregation
                           │
                           ▼
            ┌────────────────────────────┐
            │ RecommendationModelMetric  │
            │ (NEW)                      │
            │                            │
            │ metric_date = 2024-04-07   │
            │ 🆕 total_recommendations  │
            │ 🆕 successful_recs = 85   │
            │ 🆕 avg_accuracy = 85%     │
            │ 🆕 avg_days_to_interact   │
            │ 🆕 cuisine_match_success  │
            │ 🆕 price_match_success    │
            │ 🆕 dietary_match_success  │
            │                            │
            │ (shows system improving)   │
            └────────────────────────────┘
```

---

## Weight Adjustment Algorithm

```
┌──────────────────────────────────────────────────────────────────┐
│           WEIGHT ADJUSTMENT ALGORITHM (Simplified)               │
└──────────────────────────────────────────────────────────────────┘

Input: User's last 90 days of recommendations and interactions

Step 1: Categorize Recommendations
────────────────────────────────
  Recommendations: [
    {restaurant_id: 1, cuisine: "italian", price: "$$", status: "interacted"},
    {restaurant_id: 2, cuisine: "mexican", price: "$", status: "ignored"},
    {restaurant_id: 3, cuisine: "italian", price: "$$", status: "interacted"},
    ...
  ]

Step 2: Calculate Success Rates by Type
─────────────────────────────────────────
  Italian recommendations:   3/4 successful = 75%
  Mexican recommendations:   1/5 successful = 20%
  $$ price recommendations:  2/3 successful = 67%
  $ price recommendations:   2/6 successful = 33%

Step 3: Compare to Baseline
────────────────────────────
  Baseline interaction rate: 50%
  
  Italian: 75% - 50% = +25% above baseline → BOOST weight
  Mexican: 20% - 50% = -30% below baseline → REDUCE weight
  $$: 67% - 50% = +17% above baseline → BOOST weight
  $: 33% - 50% = -17% below baseline → REDUCE weight

Step 4: Apply Conservative Adjustments
───────────────────────────────────────
  Adjustment factor: 5% per iteration (prevents over-fitting)
  
  cuisine_weight (Italian focus):
    Before: 1.0
    Adjustment: +5% (conservative)
    After: 1.05  ✓
  
  price_weight ($$ focus):
    Before: 1.0
    Adjustment: +5%
    After: 1.05  ✓
  
  dietary_weight (if no pattern):
    Before: 1.0
    Adjustment: 0% (no change)
    After: 1.0  →

Step 5: Normalize and Validate
───────────────────────────────
  Sum of all weights: 1.05 + 0.95 + 1.05 + 1.0 + 1.2 + 0.5 = 5.75
  (Weights are independent, not required to sum to 1.0)
  
  Each weight within bounds [0.5, 2.0]? ✓ YES

Step 6: Store Updated Weights
──────────────────────────────
  UserPreference updated:
    cuisine_weight = 1.05 (was 1.0)
    price_weight = 1.05 (was 1.0)
    recommendation_model_version = 3 (was 2)
    last_recommendation_improvement_at = now
    learning_data_quality_score = 85%

  Result: Next recommendations use improved weights
          (Italian + $$ restaurants score higher)
```

---

## Implementation Checklist

```
PHASE 1: DATA MODELS & MIGRATION
─────────────────────────────────
☐ Add UserInteractionHistory model
  ├─ Fields: user, restaurant, interaction_type, satisfaction_score, etc.
  ├─ Meta: Indexes on (user, created_at), (restaurant, created_at)
  └─ Methods: interaction_weight, days_since_interaction
  
☐ Add RecalculatedRecommendation model
  ├─ Fields: user, restaurant, recommendation_score, accuracy_feedback, etc.
  ├─ Meta: Indexes on (user, created_at), (accuracy_feedback, created_at)
  └─ Methods: is_accurate, calculate_accuracy_from_interactions()
  
☐ Add RecommendationModelMetric model
  ├─ Fields: metric_date, total_recommendations, successful_count, accuracy, etc.
  ├─ Meta: Daily metrics storage
  └─ Methods: month_over_month_improvement
  
☐ Enhance UserPreference model
  ├─ Add 6 learned weight fields (cuisine, dietary, price, etc.)
  ├─ Add recommendation metrics fields
  ├─ Add learning tracking timestamps
  ├─ New Meta indexes
  └─ New Methods: recommendation_success_rate, has_enough_data_for_learning()
  
☐ Create & apply migrations
  └─ python manage.py makemigrations
  └─ python manage.py migrate


PHASE 2: LEARNING ALGORITHM
──────────────────────────────
☐ Enhance recommend_restaurants_for_user() function
  ├─ Add use_learning=True parameter
  ├─ Replace calculate_score with enhanced version
  ├─ Apply learned weights to each component
  └─ Add historical satisfaction boost
  
☐ Add calculate_historical_satisfaction_for_restaurant()
  ├─ Get user's past reviews of similar restaurants
  ├─ Calculate normalized satisfaction (-2 to +2)
  └─ Return boost for current recommendation
  
☐ Add calculate_time_weighted_interaction_boost()
  ├─ Get recent interactions with restaurant
  ├─ Apply time weighting (recent = 2x)
  └─ Return boost (0 to +1)
  
☐ Add record_recommendations_for_accuracy_tracking()
  ├─ Create RecalculatedRecommendation records
  ├─ Store scores and ranks
  └─ Enable future accuracy measurement


PHASE 3: AUTOMATION & SIGNALS
─────────────────────────────
☐ Enhance post_save signal for Review
  ├─ Create UserInteractionHistory
  ├─ Update RecalculatedRecommendation accuracy
  └─ Trigger recommendation recalculation
  
☐ Add recalculate_user_recommendation_model() function
  ├─ Analyze recent recommendations (90 days)
  ├─ Calculate success rates
  ├─ Adjust weights if success_rate < 30%
  └─ Update model version
  
☐ Add _adjust_weights_for_better_accuracy() helper
  ├─ Compare successful vs unsuccessful recommendations
  ├─ Identify which characteristics work
  └─ Apply conservative 5% adjustments


PHASE 4: BATCH PROCESSING
──────────────────────────
☐ Create management command: recalculate_recommendations.py
  ├─ handle(): Main entry point
  ├─ _recalculate_for_user(): Recalculate single user
  └─ _calculate_daily_metrics(): Compute daily metrics
  
☐ Set up cron/scheduler
  └─ Daily run: python manage.py recalculate_recommendations


PHASE 5: INTERACTION LOGGING
──────────────────────────────
☐ Modify restaurant_detail view
  ├─ Log UserInteractionHistory on view
  └─ Type: 'profile_view'
  
☐ Modify review creation view
  ├─ Log UserInteractionHistory after review save
  ├─ Extract satisfaction from review
  ├─ Mark was_recommended if applicable
  └─ Type: 'review_submitted'
  
☐ Optional: Modify recommendation endpoints
  ├─ Log recommendation_clicked events
  └─ Track recommendation rank


PHASE 6: TESTING
────────────────
☐ Add test_interaction_history_created_on_review()
☐ Add test_recommendation_weights_update_after_review()
☐ Add test_recommendations_change_after_interaction()
☐ Add test_recent_interactions_weighted_higher()
☐ Add test_historical_satisfaction_influences_recommendations()
☐ Add test_accuracy_tracking_records_created()
☐ Add test_recommendation_model_metrics_calculated()
☐ Add test_learning_improves_over_time()
☐ Add test_enough_data_required_for_learning()
☐ Add test_recommendation_success_rate_calculated()


PHASE 7: VERIFICATION & POLISH
───────────────────────────────
☐ Run full test suite
☐ Test performance (recommendations < 500ms)
☐ Verify migrations work on fresh DB
☐ Test with production-like data volumes
☐ Document learning algorithm
☐ Create admin views for metrics tracking
☐ Optional: Add metric dashboard
☐ Optional: Add user-facing feedback form
```

---

## Success Indicators

```
✅ SYSTEM RECALCULATES AFTER NEW RATINGS
   - Review signal fired within 100ms
   - RecalculatedRecommendation updated within 1s
   - Preference weights changed (observable)

✅ UPDATED RECOMMENDATIONS REFLECT RECENT ACTIVITY
   - Recommendation 1 before: Restaurant A
   - User rates Restaurant B (similar type) 5/5
   - Recommendation 1 after: Restaurant B or similar
   (Order changed = SUCCESS)

✅ HISTORICAL DATA CONTRIBUTES TO LEARNING
   - User has 10 Italian restaurant reviews (avg 4.5/5)
   - Italian restaurants score +2 boost
   - Verifiable in recommendation breakdown

✅ ACCURACY IMPROVES OVER TIME
   - Month 1: 45% of recommendations get interactions
   - Month 2: 52% of recommendations get interactions
   - Month 3: 58% of recommendations get interactions
   (Trending up = SUCCESS)

✅ RECOMMENDATIONS CHANGE AFTER INTERACTION
   - Test: Get recs → Rate restaurant → Get recs again
   - Assert: Similar restaurants ranked higher
   - Measurable change = SUCCESS

✅ END-TO-END TESTED
   - Full user journey tested
   - All components integrated
   - Acceptance criteria met = SUCCESS
```

