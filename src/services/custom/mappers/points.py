def _map_point(point_with_company_name):
    point, company_name = point_with_company_name
    return {
        "id": point.id,
        "company": company_name,
        "country": point.RU_country,
        "name": point.RU_city,
    }

def map_points(points_with_company_name):
    return map(_map_point, points_with_company_name)
