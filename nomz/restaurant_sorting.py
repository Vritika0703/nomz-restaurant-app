"""
Shared restaurant list ordering for map API and search views.
"""

from __future__ import annotations

from django.db.models import Case, Count, F, IntegerField, QuerySet, When

# Backward-compatible aliases (map UI historically used score_* / name_*).
_SORT_ALIASES: dict[str, str] = {
    "score_desc": "composite_desc",
    "score_asc": "composite_asc",
}


def normalize_sort_key(sort_by: str) -> str:
    raw = (sort_by or "").strip()
    return _SORT_ALIASES.get(raw, raw) or "composite_desc"


def _price_rank_annotation():
    return Case(
        When(price_range="$", then=1),
        When(price_range="$$", then=2),
        When(price_range="$$$", then=3),
        When(price_range="$$$$", then=4),
        default=99,
        output_field=IntegerField(),
    )


def sort_restaurant_queryset(queryset: QuerySet, sort_by: str) -> QuerySet:
    """
    Apply ordering at the database. Uses grade_score_latest as inspection-based
    rating (higher is better). Popularity is proxied by inspection record count.
    """
    key = normalize_sort_key(sort_by)

    if key == "composite_desc":
        return queryset.order_by(F("composite_score").desc(nulls_last=True), "name")
    if key == "composite_asc":
        return queryset.order_by(F("composite_score").asc(nulls_last=True), "name")
    if key == "rating_desc":
        return queryset.order_by(F("grade_score_latest").desc(nulls_last=True), "name")
    if key == "rating_asc":
        return queryset.order_by(F("grade_score_latest").asc(nulls_last=True), "name")
    if key == "price_asc":
        return queryset.annotate(_sort_price_rank=_price_rank_annotation()).order_by(
            "_sort_price_rank", "name"
        )
    if key == "price_desc":
        return queryset.annotate(_sort_price_rank=_price_rank_annotation()).order_by(
            "-_sort_price_rank", "name"
        )
    if key == "popularity_desc":
        return queryset.annotate(_sort_popularity=Count("inspections")).order_by(
            "-_sort_popularity", "name"
        )
    if key == "popularity_asc":
        return queryset.annotate(_sort_popularity=Count("inspections")).order_by(
            "_sort_popularity", "name"
        )
    if key == "name_asc":
        return queryset.order_by("name")
    if key == "name_desc":
        return queryset.order_by("-name")

    return queryset.order_by(F("composite_score").desc(nulls_last=True), "name")


def recommend_restaurants_for_user(user, limit=10):
    """Return a list of recommended restaurants based on user preferences."""
    from .models import Restaurant, UserPreference

    try:
        prefs = user.preferences
    except UserPreference.DoesNotExist:
        return []

    if not prefs.favorite_cuisines and not prefs.dietary_restrictions and not prefs.price_preference:
        return []

    base_qs = Restaurant.objects.filter(is_active=True, is_flagged=False)

    def calculate_score(restaurant):
        score = 0
        matched = False

        # cuisine match
        if prefs.favorite_cuisines and restaurant.cuisine_type in prefs.favorite_cuisines:
            score += 5
            matched = True

        # price match
        if prefs.price_preference and restaurant.price_range == prefs.price_preference:
            score += 3
            matched = True

        # neighborhood match
        if prefs.neighborhood_preference and prefs.neighborhood_preference.strip():
            pref_nh = prefs.neighborhood_preference.strip().lower()
            if (restaurant.neighborhood and restaurant.neighborhood.lower() == pref_nh) or (
                restaurant.borough and restaurant.borough.lower() == pref_nh
            ):
                score += 2
                matched = True

        # dietary matching by cuisine type and tags
        dietary = [d.lower() for d in (prefs.dietary_restrictions or [])]
        if dietary:
            restaurant_tags = []
            if restaurant.cuisine_type:
                restaurant_tags.append(restaurant.cuisine_type.lower())
            if restaurant.cuisine_tags:
                restaurant_tags.extend([str(x).lower() for x in restaurant.cuisine_tags])

            if "vegan" in dietary and "vegan" in restaurant_tags:
                score += 4
                matched = True
            elif "vegetarian" in dietary and "vegetarian" in restaurant_tags:
                score += 3
                matched = True
            elif "gluten-free" in dietary and "gluten-free" in restaurant_tags:
                score += 2
                matched = True
            elif "halal" in dietary and "halal" in restaurant_tags:
                score += 2
                matched = True
            elif "kosher" in dietary and "kosher" in restaurant_tags:
                score += 2
                matched = True

        if not matched:
            return 0

        # add normalized restaurant quality
        if restaurant.composite_score is not None:
            try:
                score += float(restaurant.composite_score) / 10.0
            except (TypeError, ValueError):
                pass

        return score

    scored = [(calculate_score(r), r) for r in base_qs]
    scored = sorted(scored, key=lambda x: (x[0], x[1].composite_score or 0), reverse=True)

    # remove zero-score entries (no matching preference traits)
    filtered = [r for (points, r) in scored if points > 0]
    return filtered[:limit]
