from __future__ import annotations

from django.db.models import Q

from .models import Restaurant


def _choice_maps() -> tuple[dict[str, str], dict[str, str]]:
    key_to_label = {
        str(key).strip().lower(): str(label).strip()
        for key, label in Restaurant.CUISINE_CHOICES
    }
    label_to_key = {label.lower(): key for key, label in key_to_label.items()}
    return key_to_label, label_to_key


def _clean_cuisine_tags(tags) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in tags or []:
        tag = str(item).strip()
        if not tag:
            continue
        lowered = tag.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned.append(tag)
    return cleaned


def normalize_cuisine_key(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None

    token = str(raw_value).strip().lower()
    if not token:
        return None

    key_to_label, label_to_key = _choice_maps()
    if token in key_to_label:
        return token
    return label_to_key.get(token)


def cuisine_label_for_key(cuisine_key: str | None) -> str:
    if not cuisine_key:
        return ""
    key_to_label, _ = _choice_maps()
    return key_to_label.get(cuisine_key.lower(), "")


def restaurant_cuisine_label(restaurant: Restaurant) -> str:
    cuisine_key = normalize_cuisine_key(restaurant.cuisine_type)
    if cuisine_key and cuisine_key != "other":
        return cuisine_label_for_key(cuisine_key)

    legacy_cuisine = (restaurant.cuisine or "").strip()
    if legacy_cuisine:
        return legacy_cuisine

    tags = _clean_cuisine_tags(restaurant.cuisine_tags)
    if tags:
        return ", ".join(tags[:3])

    if cuisine_key:
        return cuisine_label_for_key(cuisine_key)
    return ""


def restaurant_cuisine_tags_for_display(restaurant: Restaurant) -> list[str]:
    tags = _clean_cuisine_tags(restaurant.cuisine_tags)
    label = restaurant_cuisine_label(restaurant)
    if not label:
        return tags
    if any(tag.lower() == label.lower() for tag in tags):
        return tags
    return [label, *tags]


def synchronize_restaurant_cuisine_fields(
    restaurant: Restaurant,
) -> tuple[str, list[str]]:
    tags = _clean_cuisine_tags(restaurant.cuisine_tags)
    cuisine_text = (restaurant.cuisine or "").strip()
    cuisine_key = normalize_cuisine_key(restaurant.cuisine_type)
    key_to_label, _ = _choice_maps()

    if cuisine_key and cuisine_key != "other":
        selected_label = key_to_label[cuisine_key]
        filtered_non_primary: list[str] = []
        for tag in tags:
            tag_key = normalize_cuisine_key(tag)
            if tag_key and tag_key != cuisine_key:
                # Remove stale cuisine-category tags that conflict with primary type.
                continue
            if tag.lower() in {selected_label.lower(), cuisine_key}:
                continue
            filtered_non_primary.append(tag)

        return selected_label, [selected_label, *filtered_non_primary]

    return cuisine_text, tags


def cuisine_filter_q(raw_value: str) -> Q:
    value = (raw_value or "").strip()
    if not value:
        return Q()

    cuisine_key = normalize_cuisine_key(value)
    if cuisine_key == "other":
        return Q(cuisine_type__iexact="other")

    if cuisine_key:
        label = cuisine_label_for_key(cuisine_key)
        return Q(cuisine_type__iexact=cuisine_key) | (
            Q(cuisine_type__iexact="other")
            & (
                Q(cuisine__iexact=label)
                | Q(cuisine__iexact=cuisine_key)
                | Q(cuisine_tags__icontains=label)
                | Q(cuisine_tags__icontains=cuisine_key)
            )
        )

    return Q(cuisine_type__iexact="other") & (
        Q(cuisine__icontains=value) | Q(cuisine_tags__icontains=value)
    )


def cuisine_search_q(search: str) -> Q:
    query = (search or "").strip()
    if not query:
        return Q()

    base = Q(cuisine__icontains=query) | Q(cuisine_type__icontains=query)
    cuisine_key = normalize_cuisine_key(query)
    if cuisine_key:
        return base | cuisine_filter_q(query)
    return base | Q(cuisine_tags__icontains=query)


def sync_restaurant_search_index(restaurant: Restaurant) -> None:
    if not restaurant.pk:
        return

    from .models import RestaurantSearch

    search_name = (restaurant.name or "").strip()[:200]
    if not search_name:
        return

    neighborhood = (restaurant.neighborhood or restaurant.borough or "").strip()[:100]
    cuisine = restaurant_cuisine_label(restaurant)
    if not cuisine:
        cuisine = ", ".join(restaurant_cuisine_tags_for_display(restaurant)[:3])
    cuisine = cuisine[:100]

    defaults = {
        "neighborhood": neighborhood,
        "description": restaurant.description or "",
        "cuisine": cuisine,
    }

    existing = RestaurantSearch.objects.filter(name=search_name).order_by("id")
    primary = existing.first()
    if primary is None:
        RestaurantSearch.objects.create(name=search_name, **defaults)
        return

    for key, value in defaults.items():
        setattr(primary, key, value)
    primary.save(update_fields=list(defaults.keys()))
