def _map_container(container):
    return {
        "id": container.id,
        "type": container.type.value,
        "size": container.size,
        "weight_from": container.weight_from,
        "weight_to": container.weight_to,
        "name": container.name,
    }


def map_containers(containers):
    return map(_map_container, containers)
