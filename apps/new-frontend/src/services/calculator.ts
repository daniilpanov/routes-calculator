import { deserializeIds, serializeIds } from "./points";
import { getRoutes as fetchRoutes } from "@/api_helpers/routes";
import { RouteType } from "@/interfaces/Routes";
import { convertToCurrentRate } from "@/services/rates";
import { useRates } from "@/stores/rates";
import { useRoutes } from "@/stores/routes";

import type { ICalculatorPayload, ICalculatorPayloadWithCurrency } from "@/interfaces/CalculatorPayload";
import type {
    IMultiPriceSegment,
    ISinglePriceSegment,
    PriceDescriptor,
    PriceRange,
    RouteDescriptor,
    RouteExtendedDescriptor,
} from "@/interfaces/Routes";

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

    const {
        multi_service_routes: multiService,
        one_service_routes: oneService,
    } = await fetchRoutes({
        dispatchDate: payload.date,
        showAllRoutes: payload.showAllRoutes,
        departureInternalIds,
        destinationInternalIds,
        departureExternalIds,
        destinationExternalIds,
        containerType: payload.containerType,
        cargoWeight: payload.containerWeight,
        currency: currentRate,
    });

    useRoutes().setRoutes({
        oneService: processRoutes(oneService),
        multiService: processRoutes(multiService),
    });
}

export function revalidateRoutes() {
    const routes = useRoutes().routes;
    if (!routes)
        return;

    const { multiService, oneService } = routes;

    useRoutes().setRoutes({
        oneService: processRoutes(oneService),
        multiService: processRoutes(multiService),
    });
}

export const clearRoutes = () => useRoutes().setRoutes();

function processRoutes(routes: (RouteDescriptor | RouteExtendedDescriptor)[]): RouteExtendedDescriptor[] {
    const result: RouteExtendedDescriptor[] = Array.from({ length: routes.length });

    for (const key in routes) {
        const route = routes[key];
        if (!route)
            continue;

        let minSumPrice: number = 0, minSumPriceWithConv: number = 0;
        let maxSumPrice: number = 0, maxSumPriceWithConv: number = 0;

        for (const segment of route[0]) {
            if ((segment as ISinglePriceSegment).price) {
                const singlePriceSegment = segment as ISinglePriceSegment;

                // Without conversation percents
                const [inc] = convertToCurrentRate(singlePriceSegment.price, singlePriceSegment.currency);

                minSumPrice += inc;
                maxSumPrice += inc;
                // Without conversation percents
                minSumPriceWithConv += inc;
                maxSumPriceWithConv += inc;
            } else {
                const multiPriceSegment = segment as IMultiPriceSegment;
                if (multiPriceSegment.type === RouteType.SEA_RAIL) {
                    for (const price of multiPriceSegment.prices) {
                        const [inc, incWithConv] = convertToCurrentRate(price.value, price.currency, price.conversation_percents);

                        minSumPrice += inc;
                        maxSumPrice += inc;

                        minSumPriceWithConv += incWithConv;
                        maxSumPriceWithConv += incWithConv;
                    }
                } else {
                    let minLocalPrice: number | undefined = undefined,
                        minLocalPriceWithConv: number | undefined = undefined;
                    let maxLocalPrice: number | undefined = undefined,
                        maxLocalPriceWithConv: number | undefined = undefined;

                    for (const price of multiPriceSegment.prices) {
                        const [val, valWithConv] = convertToCurrentRate(price.value, price.currency, price.conversation_percents);

                        if (minLocalPrice === undefined || minLocalPrice > val)
                            minLocalPrice = val;
                        if (maxLocalPrice === undefined || maxLocalPrice < val)
                            maxLocalPrice = val;

                        if (minLocalPriceWithConv === undefined || minLocalPriceWithConv > valWithConv)
                            minLocalPriceWithConv = valWithConv;
                        if (maxLocalPriceWithConv === undefined || maxLocalPriceWithConv < valWithConv)
                            maxLocalPriceWithConv = valWithConv;
                    }

                    minSumPrice += minLocalPrice ?? 0;
                    maxSumPrice += maxLocalPrice ?? 0;

                    minSumPriceWithConv += minLocalPriceWithConv ?? 0;
                    maxSumPriceWithConv += maxLocalPriceWithConv ?? 0;
                }
            }
        }

        const drop = route[1];
        if (drop?.price) {
            const [inc, incWithConv] = convertToCurrentRate(drop.price, drop.currency, drop.conversation_percents);

            minSumPrice += inc;
            maxSumPrice += inc;

            minSumPriceWithConv += incWithConv;
            maxSumPriceWithConv += incWithConv;
        }

        result[key] = [
            route[0],
            route[1],
            route[2],
            (maxSumPrice - minSumPrice > Number.EPSILON
                ? [minSumPrice, maxSumPrice]
                : minSumPrice) as PriceDescriptor,
            (maxSumPriceWithConv - minSumPriceWithConv > Number.EPSILON
                ? [minSumPriceWithConv, maxSumPriceWithConv]
                : minSumPriceWithConv) as PriceDescriptor,
        ];
    }

    result.sort((a: RouteExtendedDescriptor, b: RouteExtendedDescriptor) =>
        (Number.isNaN(a[4]) ? (a[4] as PriceRange)[0] : a[4] as number)
        - (Number.isNaN(b[4]) ? (b[4] as PriceRange)[0] : b[4] as number));

    return result;
}
