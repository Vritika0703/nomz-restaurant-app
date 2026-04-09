# Quick Reference: Changes Needed for Continuous Recommendation Refinement

## Summary of Changes

This user story requires implementing a **learning-based recommendation system** that continuously improves based on user interactions.

---

## 🔴 Critical Changes (Must Implement)

### 1. **Add UserInteractionHistory Model** (`nomz/models.py`)
- Tracks every user interaction (views, reviews, searches, clicks)
- Timestamp and type of interaction
- Links user to restaurant
- Enables historical analysis for learning

### 2. **Enhance UserPreference Model** (`nomz/models.py`)
- Add learning weights: `cuisine_weight`, `dietary_weight`, `price_weight`, etc.
- Track recommendation metrics: `total_recommendations_received`, `successful_recommendations`
- Add `recommendation_model_version` to track iterations
- Add `last_recommendation_recalculated_at` timestamp

### 3. **Enhance Recommendation Scoring** (`nomz/restaurant_sorting.py`)
- Modify `recommend_restaurants_for_user()` to use historical data
- **Implement time-based weighting:**
  - Recent interactions (last 30 days): 2x weight
  - 30-90 days old: 1.5x weight
  - Older: 1x weight
- **Extract user satisfaction from review ratings:**
  - Use `Review.experience_rating` to gauge satisfaction
  - Boost similar restaurants if user satisfied
- **Adjust recommendation weights dynamically** based on user's personal success patterns

### 4. **Update Signal Handlers** (`nomz/signals.py`)
- Enhance existing `refresh_score_on_review_save()` to:
  - Create `UserInteractionHistory` entry
  - Extract satisfaction score from review
  - Trigger recommendation model update
- Add new handler for tracking recommendation clicks (optional but useful)
- Create `recalculate_user_recommendations()` function

### 5. **Add Recommendation Accuracy Tracking** (`nomz/models.py`)
- Create `RecalculatedRecommendation` model to store:
  - Recommendation score at time of generation
  - Whether user interacted with recommended restaurant
  - Time to interaction (days)
  - Accuracy feedback
- This creates measurable improvement metrics

### 6. **Add Recalculation Management Command** (`nomz/management/commands/`)
- Daily task to:
  - Analyze all user interactions
  - Calculate recommendation model metrics
  - Identify which preference combinations work best
  - Update `UserPreference` weights accordingly
  - Store metrics in `RecommendationModelMetric` model

---

## 🟡 Secondary Changes (Recommended)

### 7. **Add RecommendationModelMetric Model** (`nomz/models.py`)
- Tracks system-wide metrics daily:
  - `total_recommendations_given`
  - `successful_recommendations`
  - `avg_recommendation_accuracy`
  - Cuisine/dietary/price success rates
  - Helps demonstrate improvement over time

### 8. **Update Review/Recommendation Views** (`nomz/views.py`)
- Log interaction when user views recommendations
- Log satisfaction when review is submitted
- Update recommendation feedback after each interaction

### 9. **Add API Endpoints** (`nomz/api_views.py`)
- GET `/api/recommendations/history/` - User's recommendation history
- GET `/api/recommendations/metrics/` - Accuracy metrics
- POST `/api/recommendations/feedback/` - Feedback on recommendations

---

## 📋 Testing Requirements

### Unit Tests to Add (`nomz/test_recommendations.py`)
```python
- test_interaction_history_creation()
- test_recommendation_weights_update_after_review()
- test_historical_data_influences_recommendations()
- test_recent_interactions_weighted_higher()
- test_user_satisfaction_boosts_similar_restaurants()
- test_recommendation_accuracy_tracking()
- test_model_recalculation_command()
```

### Integration Tests
- **Verify the learning loop works:**
  1. Get initial recommendations
  2. User submits review with high rating
  3. Get new recommendations
  4. Verify new recommendations reflect preference from review

---

## 🔄 Data Flow Diagram

```
User interacts with restaurant
         ↓
[Signal Handler triggered]
         ↓
Create UserInteractionHistory entry
         ↓
Extract satisfaction score from Review
         ↓
Update UserPreference recommendation weights
         ↓
[Next time recommendations generated]
         ↓
recommend_restaurants_for_user() uses:
  - Preference WEIGHTS (from learning)
  - Historical interactions (boost similar to liked)
  - Time-weighted scoring (recent = more important)
         ↓
Generate improved recommendations
         ↓
RecalculatedRecommendation stores accuracy data
         ↓
[Daily batch job]
         ↓
Recalculate model metrics & further optimize weights
```

---

## 📊 Success Metrics (Definition of Done)

| Criterion | How to Verify |
|-----------|---------------|
| **Recalculates after ratings** | Signal handler logs + DB query shows updated weights |
| **Updated recommendations reflect activity** | Test: submit review → recommendations change |
| **Historical data contributes** | UserInteractionHistory populated + visible in scoring logic |
| **Accuracy improves over time** | RecalculatedRecommendation.accuracy_feedback improves month-over-month |
| **Recommendations change after interaction** | Unit test verifies different results before/after |
| **End-to-end tested** | Full integration test with multiple users, reviews, and recommendations |

---

## 📁 Files to Modify/Create

| File | Type | Purpose |
|------|------|---------|
| `nomz/models.py` | Modify | Add 3-4 new models + enhance UserPreference |
| `nomz/signals.py` | Modify | Add interaction tracking + recalculation triggers |
| `nomz/restaurant_sorting.py` | Modify | Enhance recommendation algorithm with historical learning |
| `nomz/management/commands/recalculate_recommendations.py` | Create | Daily batch recalculation job |
| `nomz/test_recommendations.py` | Modify | Add tests for continuous refinement |
| `nomz/views.py` | Modify | Add interaction logging |
| `nomz/migrations/00XX_xxx.py` | Create | Migration for new models |

---

## 🚀 Implementation Order (Recommended)

1. Add `UserInteractionHistory` model
2. Add fields to `UserPreference` model
3. Create migration
4. Update signal handlers to create interaction history
5. Update Review views to log satisfaction
6. Enhance `recommend_restaurants_for_user()` algorithm
7. Add `RecalculatedRecommendation` model (optional but useful)
8. Create management command for recalculation
9. Add comprehensive tests
10. Create `RecommendationModelMetric` tracking (optional)

---

## 💡 Key Concepts

**Continuous Refinement Loop:**
```
Preferences → Recommendations → User Reviews → 
Interaction History → Learn from Patterns → 
Adjust Weights → Better Recommendations
```

**Time-Based Weighting:**
- Recent data is more relevant (2x weight)
- Medium-term data moderately relevant (1.5x weight)
- Older data less relevant (1x weight)

**Satisfaction Pattern Recognition:**
- If user rated Italian restaurants 4.5/5 average → boost Italian in recommendations
- If user rated Mexican restaurants 2/5 average → reduce Mexican recommendations
- If user books many reservations at $$$ restaurants → prioritize those

**Learning Mechanism:**
- Track which recommendations led to interactions (views, reviews, reservations)
- Calculate success rate for each preference combination
- Dynamically adjust weights to favor combinations with higher success rates

