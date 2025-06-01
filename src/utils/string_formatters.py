def union_country_and_name(country, name):
    if country and name:
        return country + ', ' + name
    return name or country
