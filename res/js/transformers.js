function mapSegmentType(type) {
    switch (type) {
        case 1: return 'rail';
        case 2: return 'sea';
        case 3: return 'truck';
        default: return 'unknown';
    }
}

function transformResponseData(routes) {
    return routes.map(route => ({
        dateFrom: route.DateFrom,
        dateTo: route.DateTo,
        beginCond: route.BeginCond,
        finishCond: route.FinishCond,
        containers: route.Containers.map(c => ({ name: c.ContainerName })),
        segments: route.Segments.map(segment => ({
            segmentOrder: segment.SegmentOrder,
            type: mapSegmentType(segment.SegmentType),
            from: { name: segment.BeginLocName },
            to: { name: segment.FinishLocName },
            price: segment.Containers.map(c => ({
                containerId: c.ContainerCode,
                sum: c.Price,
                currency: c.Currency
            }))
        })),
        services: route.Services.map(service => ({
            name: service.ServiceName,
            checked: service.checked || service.Default,
            isRequired: service.Default,
            price: service.ContPrice.map(p => ({
                containerId: p.ContainerCode,
                sum: p.Price,
                currency: p.Currency
            }))
        }))
    }));
}
