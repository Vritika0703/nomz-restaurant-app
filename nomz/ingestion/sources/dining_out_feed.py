from __future__ import annotations

from typing import Dict, Iterable
from nomz.ingestion.sources.nyc_endpoints import DINING_OUT
from nomz.ingestion.utils.normalization import (
    first_non_empty,
    normalize_text,
    split_list_fields,
    to_decimal_str,
    to_str,
)


def _coerce_phone(value: object) -> str:
    if value in (None, ""):
        return ""
    phone = to_str(value).replace(" ", "").replace("-", "")
    return phone


def _extract_coordinates(row: Dict) -> tuple[str | None, str | None]:
    lat = to_decimal_str(row.get("latitude"))
    lon = to_decimal_str(row.get("longitude"))
    if lat and lon:
        return lat, lon

    location = row.get("location")
    if isinstance(location, str):
        cleaned = location.replace("POINT", "").replace("(", "").replace(")", "")
        parts = [p.strip() for p in cleaned.split() if p.strip()]
        if len(parts) >= 2:
            return to_decimal_str(parts[1]), to_decimal_str(parts[0])
    elif isinstance(location, dict):
        lat = lat or to_decimal_str(location.get("latitude"))
        lon = lon or to_decimal_str(location.get("longitude"))
        return lat, lon

    return None, None


def normalize_dining_out_row(row: Dict) -> Dict:
    name = first_non_empty(
        row,
        ["business_legal_name", "assumed_name_s", "name", "restaurant_name", "dba"],
    )
    street = first_non_empty(row, ["street", "street_name", "address"])
    building = first_non_empty(row, ["building_number", "building", "house_number"])
    zip_code = first_non_empty(row, ["postcode", "zip", "zipcode", "postal_code"])
    borough = first_non_empty(row, ["borough", "boro"])
    city = first_non_empty(row, ["city"])
    if city and not borough:
        borough = city

    lat, lon = _extract_coordinates(row)
    cuisines = split_list_fields(first_non_empty(row, ["cuisine", "cuisine_type", "cuisine_style"]))
    raw_lat, raw_lon = lat, lon

    return {
        "source": "DINING_OUT",
        "source_external_id": first_non_empty(row, ["id", "camis", "location_name", "business_legal_name"]),
        "name": name,
        "name_normalized": normalize_text(name),
        "building": building,
        "street": street,
        "zip_code": zip_code,
        "borough": borough,
        "phone": _coerce_phone(first_non_empty(row, ["phone", "phone_number"])),
        "website": first_non_empty(row, ["website", "webaddress", "url"]),
        "latitude": raw_lat,
        "longitude": raw_lon,
        "cuisine_tags": cuisines,
        "raw_payload": row,
    }


def stream_dining_out_rows(client) -> Iterable[Dict]:
    for row in client.fetch_all(DINING_OUT):
        normalized = normalize_dining_out_row(row)
        if not normalized["name"]:
            continue
        if first_non_empty(normalized, ["name", "street", "zip_code"]):
            yield normalized
