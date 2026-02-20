def _map_point(item):
    point_id, point_name, point_country, point_ru_name, point_ru_country, company_id, company_name = item
    return {
        "id": point_id,
        "company": {"id": company_id, "name": company_name},
        "ports": [],
        "translates": {
            "ru": {
                "country": point_ru_country,
                "name": point_ru_name,
            },
            "en": {
                "country": point_country,
                "name": point_name,
            },
        },
    }


def _map_point_id(point):
    return point.id


def map_points(points):
    return map(_map_point, points)


def map_point_ids(points):
    return map(_map_point_id, points)
