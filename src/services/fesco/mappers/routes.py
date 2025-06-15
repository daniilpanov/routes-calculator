from .containers import _map_container

_segment_types = {
    1: 'rail',
    2: 'sea',
    3: 'truck',
}


def _map_segment(segment):
    return ({
        'type': _segment_types.get(segment['SegmentType']),
        'startPointCountry': segment['BeginCountryName'],
        'startPointName': segment['BeginLocName'],
        'endPointCountry': segment['FinishCountryName'],
        'endPointName': segment['FinishLocName'],
        'price': segment['Containers'][0]['Price'],
        'currency': segment['Containers'][0]['Currency'],
    })


def _map_route(route):
    res = []
    for segm in map(_map_segment, route.get('Segments', [])):
        res.append(
            {
                'company': 'FESCO',
                'effectiveFrom': route['DateFrom'],
                'effectiveTo': route['DateTo'],
                'container': _map_container(route['Containers'][0]),
                'services': {},
            } | segm | ({
                'beginCond': route['BeginCond'],
                'finishCond': route['FinishCond'],
            } if segm['type'] == 'sea' else {})
        )
    return res

def map_routes(routes):
    return map(_map_route, routes)
