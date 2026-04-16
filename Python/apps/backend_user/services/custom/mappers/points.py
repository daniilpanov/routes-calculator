# V1

def _map_point_v1(item):
    point, company = item
    return {
        "id": point.id,
        "company": company.name,
        "country": point.RU_country,
        "name": point.RU_city,
    }


def map_points_v1(points):
    return map(_map_point_v1, points)


# V2


def _map_point_v2(item):
    point, company = item
    return {
        "id": point.id,
        "company": {"id": company.id, "name": company.name},
        "ports": [],
        "translates": {
            "ru": {
                "country": point.RU_country,
                "name": point.RU_city,
            },
            "en": {
                "country": point.country,
                "name": point.city,
            },
        },
    }


def map_points_v2(points):
    return map(_map_point_v2, points)
