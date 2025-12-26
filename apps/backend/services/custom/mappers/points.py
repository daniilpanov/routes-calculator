def _map_point(item):
    point, company = item
    return {
        "id": point.id,
        "company": company,
        "country": point.RU_country,
        "name": point.RU_city,
    }


def map_points(points):
    return map(_map_point, points)
