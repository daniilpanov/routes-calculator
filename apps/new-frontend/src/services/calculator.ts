import { deserializeIds } from "./points";

export function deserializeCalculatorQueryParams(query: Record<string, unknown>) {
    const params: Record<string, unknown> = {};

    if (query.currency) params.currency = query.currency;

    if (query.date && !Number.isNaN(new Date(query.date as string).getDate()))
        params.date = query.date;

    if (query.showAllRoutes) params.showAllRoutes = query.showAllRoutes === "true";

    if (query.departureIds) {
        params.departureIds = deserializeIds(query.departureIds as string);

        if (query.destinationIds)
            params.destinationIds = deserializeIds(query.destinationIds as string);
    }

    if (query.type) params.containerType = query.type;

    if (query.weight) params.containerWeight = Number(query.weight);

    return params;
}
