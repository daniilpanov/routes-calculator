import { deserializeIds, serializeIds } from "./points";
import { getRoutes as fetchRoutes } from "@/api_helpers/routes";
import { useRates } from "@/stores/rates";
import { useRoutes } from "@/stores/routes";

import type { ICalculatorPayload, ICalculatorPayloadWithCurrency } from "@/interfaces/CalculatorPayload";

export const serializeCalculatorQueryParams = (payload: ICalculatorPayloadWithCurrency) => ({
    date: payload.date,
    showAllRoutes: payload.showAllRoutes === undefined ? undefined : payload.showAllRoutes ? "true" : "false",
    departureIds: payload.departureIds ? serializeIds(payload.departureIds) : undefined,
    destinationIds: payload.departureIds && payload.destinationIds ? serializeIds(payload.destinationIds) : undefined,
    type: payload.containerType,
    weight: payload.containerWeight,
    currency: payload.currency,
});

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

export async function updateRoutes(payload: ICalculatorPayload) {
    if (
        !payload.date
        || payload.showAllRoutes === undefined
        || !payload.departureIds?.length
        || !payload.destinationIds?.length
        || !payload.containerType
        || !payload.containerWeight
    ) throw new Error(`Insufficient payload! ${JSON.stringify(payload)}`);

    const { currentRate } = useRates();
    if (!currentRate)
        throw new Error("No current rate!");

    const departureInternalIds: number[] = [];
    const destinationInternalIds: number[] = [];
    const departureExternalIds: string[] = [];
    const destinationExternalIds: string[] = [];

    for (const departureIdDescriptor of payload.departureIds) {
        if (departureIdDescriptor.isExternal)
            departureExternalIds.push(departureIdDescriptor.id as string);
        else
            departureInternalIds.push(departureIdDescriptor.id as number);
    }

    for (const destinationIdDescriptor of payload.destinationIds) {
        if (destinationIdDescriptor.isExternal)
            destinationExternalIds.push(destinationIdDescriptor.id as string);
        else
            destinationInternalIds.push(destinationIdDescriptor.id as number);
    }

    useRoutes().setRoutes(await fetchRoutes({
        dispatchDate: payload.date,
        showAllRoutes: payload.showAllRoutes,
        departureInternalIds,
        destinationInternalIds,
        departureExternalIds,
        destinationExternalIds,
        containerType: payload.containerType,
        cargoWeight: payload.containerWeight,
        currency: currentRate,
    }));
}

export const clearRoutes = () => useRoutes().setRoutes();
