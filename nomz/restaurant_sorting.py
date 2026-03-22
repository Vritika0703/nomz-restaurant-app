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
