def _map_point(point):
    return {
        "id": point.id,
        "company": point.company_name,
        "country": point.RU_country,
        "name": point.RU_city,
    }


def map_points(points):
    return map(_map_point, points)
