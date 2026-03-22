from __future__ import annotations

from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .filtering import (
    apply_open_now_filter,
    apply_restaurant_filters,
    parse_bool,
    restaurant_ordering,
)
from .models import Restaurant


def _safe_decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_score_text(value: Decimal | None) -> str:
    if value is None:
        return "No score"
    number = _safe_decimal_to_float(value)
    if number is None:
        return "No score"
    return f"{number:.0f}" if number.is_integer() else f"{number:.1f}"


def _coerce_float(raw_value: str) -> float | None:
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return None


@require_GET
def map_restaurant_data(request):
    """
    Return restaurant marker-ready JSON for the map UI.
    """
    queryset = apply_restaurant_filters(
        Restaurant.objects.all(),
        params=request.GET,
        require_coordinates=True,
    )

    sw_lat = _coerce_float(request.GET.get("sw_lat", "").strip())
    ne_lat = _coerce_float(request.GET.get("ne_lat", "").strip())
    sw_lng = _coerce_float(request.GET.get("sw_lng", "").strip())
    ne_lng = _coerce_float(request.GET.get("ne_lng", "").strip())
    if all(v is not None for v in (sw_lat, ne_lat, sw_lng, ne_lng)):
        queryset = queryset.filter(
            latitude__gte=sw_lat,
            latitude__lte=ne_lat,
            longitude__gte=sw_lng,
            longitude__lte=ne_lng,
        )

    limit_raw = request.GET.get("limit", "").strip()
    try:
        limit = max(1, min(int(limit_raw), 4000))
    except (TypeError, ValueError):
        limit = 1000

    sort_by = request.GET.get("sort_by", "score_desc").strip()
    ordered_queryset = queryset.order_by(*restaurant_ordering(sort_by))[:limit]
    if parse_bool(request.GET.get("open_now")):
        queryset_rows = apply_open_now_filter(ordered_queryset)
    else:
        queryset_rows = list(ordered_queryset)

    points = []
    for restaurant in queryset_rows:
        lat = _safe_decimal_to_float(restaurant.latitude)
        lon = _safe_decimal_to_float(restaurant.longitude)
        if lat is None or lon is None:
            continue

        points.append(
            {
                "id": restaurant.id,
                "name": restaurant.display_name or restaurant.name,
                "address": ", ".join(
                    part
                    for part in [
                        restaurant.building or "",
                        restaurant.street or "",
                        restaurant.borough or "",
                        restaurant.zip_code or "",
                    ]
                    if part
                ),
                "borough": restaurant.borough,
                "zip_code": restaurant.zip_code,
                "phone": restaurant.phone,
                "cuisine_tags": restaurant.cuisine_tags or [],
                "latitude": lat,
                "longitude": lon,
                "composite_score": _safe_decimal_to_float(restaurant.composite_score),
                "composite_score_label": _safe_score_text(restaurant.composite_score),
                "grade": restaurant.grade_latest or "",
                "inspected_on": (
                    restaurant.last_inspection_date.isoformat()
                    if restaurant.last_inspection_date
                    else ""
                ),
            }
        )

    return JsonResponse({"count": len(points), "results": points})
