from collections.abc import Iterator
from typing import Any

# V1


def _map_point_v1(point):
    return {
        "id": point["id"],
        "company": "FESCO",
        "country": point["country"],
        "name": point["name"],
    }


def map_points_v1(points):
    return map(_map_point_v1, points)


# V2


def _is_invalid_point(point: dict[str, Any]) -> bool:
    """
    Checks if a point should be excluded from results.

    Returns True if point contains default/dummy location indicators.
    """
    point_loc_name = point.get("name")
    return not point_loc_name or "DEFAULT LOCATION" in point_loc_name


def _map_point_v2(point: dict[str, Any]) -> dict[str, Any] | None:
    """
    Maps a single point from source format to target format.
    Dynamically includes all languages defined in language_map.

    Args:
        point: Source point dictionary
    """
    if _is_invalid_point(point):
        return None

    language_map = {
        "ru": {"name_field": "name", "country_field": "country"},
        "en": {"name_field": "nameLatin", "country_field": "countryLatin"},
        "cn": {"name_field": "nameCN", "country_field": "countryCN"},
        "vn": {"name_field": "nameVN", "country_field": "countryVN"},
    }

    result = {
        "id": point["id"],
        "company": {"id": "FESCO", "name": "FESCO"},
        "translates": {},
    }

    # Process all languages uniformly from the mapping
    for lang_code, fields in language_map.items():
        name_value = point.get(fields["name_field"])

        # Skip if name is None
        if name_value is None:
            continue

        country_value = point.get(fields["country_field"])

        result["translates"][lang_code] = {
            "country": country_value.strip() if country_value is not None else "",
            "name": name_value.strip(),
        }

    return result


def map_points_v2(points: Iterator[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    """
    Maps multiple points from source format to target format.
    Filters out invalid points and dynamically includes all available languages.

    Args:
        points: Iterator of source point dictionaries

    Returns:
        Iterator of mapped point dictionaries with dynamic language support
    """
    return filter(None, map(_map_point_v2, points))
