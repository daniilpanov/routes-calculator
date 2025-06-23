import re


def _map_container(container):
    seeking_expr = re.compile(r"\((\d+)'(.+)\)\D+(\d+)-(\d+)t$")
    data = seeking_expr.findall(container['ContainerNameEng'])
    if data:
        csize, ctype, cweight_from, cweight_to = data[0]
        csize = int(csize)
        cweight_from = int(cweight_from)
        cweight_to = int(cweight_to)
    else:
        seeking_expr = re.compile(r"\((\d+)'(.+)\)\D+(\d+)t$")
        data = seeking_expr.findall(container['ContainerNameEng'])
        if data:
            csize, ctype, cweight_to = data[0]
            csize = int(csize)
            cweight_from = 0
            cweight_to = int(cweight_to)
        else:
            seeking_expr = re.compile(r"\((\d+)'(.+)\)$")
            data = seeking_expr.findall(container['ContainerNameEng'])
            if not data:
                return None
            csize, ctype = data[0]
            csize = int(csize)
            cweight_from = None
            cweight_to = None

    return {
        'id': container['ContainerCode'],
        'company': 'FESCO',
        'type': ctype,
        'size': csize,
        'weight_from': cweight_from,
        'weight_to': cweight_to,
        'name': f"{csize}'{ctype} {int(cweight_from)}-{int(cweight_to)}t" if cweight_to else f"{csize}'{ctype}",
    }

def map_containers(containers):
    return list(sorted(
        map(_map_container, containers),
        key=lambda c: c['size'] * 100 + (c['weight_to'] or 0),
    ))
