from __future__ import annotations

from typing import Iterable

from django.utils import timezone

from nomz.ingestion.utils.score import compute_restaurant_composite_score


def refresh_restaurant_composite(restaurant):
    """
    Recompute and persist composite fields for a single restaurant.
    """
    score_data = compute_restaurant_composite_score(restaurant)
    restaurant.composite_score = score_data["composite_score"]
    restaurant.grade_latest = score_data["grade"]
    restaurant.grade_score_latest = score_data["grade_score"]
    restaurant.last_inspection_date = score_data["last_inspection_date"]
    restaurant.composite_score_calculated_at = timezone.now()
    restaurant.save(
        update_fields=[
            "composite_score",
            "grade_latest",
            "grade_score_latest",
            "last_inspection_date",
            "composite_score_calculated_at",
            "updated_at",
        ]
    )
    return score_data


def refresh_restaurants_composite(restaurants: Iterable):
    """
    Recompute and persist scores for an iterable of Restaurant objects.
    """
    refreshed = 0
    for restaurant in restaurants:
        refresh_restaurant_composite(restaurant)
        refreshed += 1
    return refreshed
