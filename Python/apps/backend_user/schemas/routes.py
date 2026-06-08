from module_shared.models.route import DropItem, RouteSegment, ServiceItem

NormalizedRoutes = list[tuple[list[RouteSegment], DropItem | None, bool, list[ServiceItem]]]
