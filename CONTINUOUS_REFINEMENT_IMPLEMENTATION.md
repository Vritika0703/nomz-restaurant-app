# Continuous Recommendation Refinement Implementation Plan

## Overview
This document outlines the changes needed to implement a continuous recommendation refinement system that improves suggestions based on user interactions over time.

## Current State Analysis

### Existing Components
1. **UserPreference Model** - Stores user preferences (cuisines, dietary, price, neighborhood)
2. **Review Model** - Captures detailed ratings (overall, food quality, service, ambience, etc.)
3. **Restaurant Model** - Has composite_score for quality evaluation
4. **recommend_restaurants_for_user()** - Current recommendation function that matches user preferences against restaurants
5. **Signal handlers** - Already refresh restaurant composite scores on review save/delete

### Limitations
- Recommendations are **static** - based only on user preferences, not historical interactions
- No tracking of **user-restaurant interaction history**
- No **learning mechanism** to improve recommendations based on past user behavior
- No timestamp-based weighting (recent interactions not prioritized)
- Recommendation scores don't account for **how satisfied** users were with past recommendations

## Implementation Changes Required

### 1. **New Models for Tracking Interactions**

#### A. UserInteractionHistory Model
Tracks all user interactions with restaurants to build historical context for learning.

```python
class UserInteractionHistory(models.Model):
    INTERACTION_TYPES = [
        ('view', 'Restaurant View'),
        ('search', 'Search Query'),
        ('review_submitted', 'Review Submitted'),
        ('review_rating_given', 'Rating Provided'),
        ('recommendation_viewed', 'Recommendation Viewed'),
        ('recommendation_clicked', 'Recommendation Clicked'),
        ('reservation', 'Reservation Made'),
        ('profile_visited', 'Profile Visited'),
    ]
    
    user = ForeignKey(User)
    restaurant = ForeignKey(Restaurant, nullable)  # nullable for search queries
    interaction_type = CharField(choices=INTERACTION_TYPES)
    
    # Attributes to capture outcome
    user_satisfaction_score = IntegerField(null=True, blank=True)  # -1, 0, +1 or 1-5
    time_spent_seconds = IntegerField(null=True)  # How long user viewed/explored
    
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['user', '-created_at']),
            Index(fields=['restaurant', '-created_at']),
            Index(fields=['user', 'restaurant', '-created_at']),
        ]
```

#### B. RecalculatedRecommendation Model
Stores recommendation snapshots to track model accuracy over time.

```python
class RecalculatedRecommendation(models.Model):
    user = ForeignKey(User)
    restaurant = ForeignKey(Restaurant)
    recommendation_score = DecimalField()  # Score from the recommendation algorithm
    
    # Learning metrics
    accuracy_feedback = IntegerField(null=True)  # Was this a good recommendation? 1=yes, 0=no, -1=bad
    days_to_interaction = IntegerField(null=True)  # Days until user interacted with restaurant
    interaction_type = CharField(max_length=50, null=True)  # view, review, reservation
    
    calculated_at = DateTimeField(auto_now_add=True)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']
        unique_together = [['user', 'restaurant', 'calculated_at']]
        indexes = [
            Index(fields=['user', '-calculated_at']),
            Index(fields=['accuracy_feedback', '-created_at']),
        ]
```

#### C. RecommendationModelMetric Model
Tracks system-wide recommendation quality metrics.

```python
class RecommendationModelMetric(models.Model):
    metric_date = DateField(auto_now_add=True)
    
    # Overall metrics
    total_recommendations_given = IntegerField(default=0)
    successful_recommendations = IntegerField(default=0)  # Led to interaction
    avg_recommendation_accuracy = DecimalField()  # % of recommendations that led to actions
    
    # Learning metrics
    avg_days_to_interaction = DecimalField(null=True)  # Avg days user takes to interact
    cuisine_match_success_rate = DecimalField()  # % of cuisine matches that convert
    price_match_success_rate = DecimalField()
    dietary_match_success_rate = DecimalField()
    
    last_recalculated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-metric_date']
```

### 2. **Enhanced UserPreference Model**

Add weight adjustments based on learning:

```python
class UserPreference(models.Model):
    # ... existing fields ...
    
    # Learning weights - adjusted based on interaction history
    cuisine_weight = DecimalField(default=1.0)  # Adjust if certain cuisines perform well
    dietary_weight = DecimalField(default=1.0)
    price_weight = DecimalField(default=1.0)
    neighborhood_weight = DecimalField(default=1.0)
    composite_score_weight = DecimalField(default=1.0)
    
    # Recommendation model metrics
    total_recommendations_received = IntegerField(default=0)
    successful_recommendations = IntegerField(default=0)
    
    last_recommendation_recalculated_at = DateTimeField(null=True)
    last_recommendation_improvement_at = DateTimeField(null=True)  # When model last improved
    
    recommendation_model_version = IntegerField(default=1)  # Track model iterations
```

### 3. **Enhanced Recommendation Scoring Algorithm**

Update `recommend_restaurants_for_user()` to incorporate:

**A. Historical Performance Weighting**
- High-rated reviews of similar restaurants increase scores
- Recent interactions (last 30 days) weighted 2x
- Interactions from 30-90 days ago weighted 1.5x
- Older interactions weighted 1x

**B. User Satisfaction Pattern Recognition**
- If user consistently rates Italian 4.5/5 but rates Japanese 2/5, boost Italian
- If user often books reservations at restaurants in certain price ranges, boost those

**C. Cuisine/Dietary Success Rate Boost**
- Track which preference combinations lead to successful interactions
- Dynamically adjust weights based on user's own success patterns

**D. Collaborative Filtering Element** (optional enhancement)
- Compare user's ratings with similar users
- Recommend restaurants liked by users with similar tastes

### 4. **Signal Handlers for Automatic Refinement**

#### A. Review/Rating Signal Enhancement
When user submits a review/rating:
1. Create `UserInteractionHistory` record (type: 'review_submitted')
2. Extract satisfaction score from review ratings
3. Create `RecalculatedRecommendation` entry if this was a recommended restaurant
4. Trigger recommendation model recalculation

#### B. Recommendation Click Signal
When user clicks on a recommendation:
1. Create `UserInteractionHistory` record (type: 'recommendation_clicked')
2. Log the recommendation score for accuracy tracking
3. Update `RecalculatedRecommendation` with interaction timestamp

#### C. Batch Recommendation Recalculation
Create management command to:
1. Run daily to recalculate recommendation weights
2. Analyze interaction patterns for all users
3. Update `RecommendationModelMetric` entries
4. Adjust preference weights in `UserPreference` model

### 5. **New/Modified Views & Endpoints**

#### A. Enhanced Restaurant Detail View
- Track when user views a recommendation
- Log interaction history
- Display if this was a recommended restaurant

#### B. Review Creation/Update
- After review save, trigger recommendation recalculation for that user
- Update satisfaction metrics
- Log recommendation accuracy

#### C. New API Endpoints (if needed)
- `/api/recommendations/history/` - Get user's recommendation history
- `/api/recommendations/metrics/` - Get user's recommendation accuracy metrics
- `/api/recommendations/feedback/` - Submit feedback on recommendation quality

### 6. **Changes to Existing Files**

| File | Changes |
|------|---------|
| `nomz/models.py` | Add 4 new models + fields to UserPreference |
| `nomz/signals.py` | Add handlers for interaction tracking and recommendation recalculation |
| `nomz/restaurant_sorting.py` | Enhance `recommend_restaurants_for_user()` with historical learning |
| `nomz/forms.py` | Add form for recommendation feedback (optional) |
| `nomz/views.py` | Add interaction logging to restaurant/recommendation views |
| `nomz/api_views.py` | Add endpoints for recommendation history/metrics |
| `nomz/management/commands/` | Add command for daily model recalculation |
| `nomz/test_recommendations.py` | Add tests for continuous refinement |

### 7. **Database Migrations**

Create migration files for:
1. New models
2. Updated UserPreference fields
3. Indexes for performance

### 8. **Testing Requirements**

#### Unit Tests
- Historical interaction tracking
- Weight adjustment calculations
- Recommendation accuracy metrics
- Signal handler triggers

#### Integration Tests
- End-to-end: User submits review → Recommendation weights updated → New recommendations reflect change
- Verify older recommendations vs newer recommendations
- Test accuracy feedback loop

#### Performance Tests
- Ensure recommendation calculation stays <500ms even with large history
- Batch recalculation performance

---

## Implementation Checklist

- [ ] Create 4 new Django models
- [ ] Add fields to UserPreference model
- [ ] Create migrations
- [ ] Update signals.py with interaction tracking
- [ ] Enhance recommendation algorithm in restaurant_sorting.py
- [ ] Add recommendation feedback mechanism to views
- [ ] Create management command for batch recalculation
- [ ] Update tests with new test cases
- [ ] Create documentation
- [ ] Performance testing

---

## Success Criteria

✅ **System recalculates recommendation scores after new ratings or reviews**
- Signal handler triggers on Review save
- Recommendation weights update within 1 second

✅ **Updated recommendations reflect recent activity**
- Recent interactions weighted higher
- User sees different recommendations after submitting a review

✅ **Historical interaction data contributes to learning logic**
- UserInteractionHistory model captures all interactions
- Scoring algorithm incorporates historical data

✅ **Recommendation accuracy improves over time (measurable criteria defined)**
- RecalculatedRecommendation tracks accuracy
- RecommendationModelMetric tracks system-wide improvement
- Success metrics: % of recommendations leading to interactions

✅ **Verified that recommendation list changes after interaction**
- Tests verify different recommendations before/after reviews
- Dashboard shows metric improvements

✅ **Tested end-to-end**
- Full integration tests of recommendation-review-recommendation cycle
- User journey tests

---

## Priority & Phasing

**Phase 1 (High Priority):**
1. UserInteractionHistory model
2. Review signal enhancement
3. Enhanced recommendation scoring
4. Tests

**Phase 2 (Medium Priority):**
5. RecalculatedRecommendation model
6. RecommendationModelMetric tracking
7. Management command for recalculation

**Phase 3 (Nice to Have):**
8. API endpoints for history/metrics
9. UI dashboard for recommendation metrics
10. Collaborative filtering

