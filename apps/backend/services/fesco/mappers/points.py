def _map_point(point):
    return {
        "id": point["id"],
        "company": {"id": "FESCO", "name": "FESCO"},
        "translates": {
            "ru": {
                "entityId": point["id"],
                "lang": "ru",
                "country": point["country_name"],
                "name": point["loc_name"],
            },
            "en": {
                "entityId": point["id"],
                "lang": "en",
                "country": point["country_name_latin"],
                "name": point["loc_name_latin"],
            },
        },
    }


def _map_point_id(point):
    return point["id"]


def map_points(points):
    return map(_map_point, points)


def map_point_ids(points):
    return map(_map_point_id, points)
