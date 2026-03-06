<script setup lang="ts">
import type { ICalculatorExtendedResult, IMultiPriceSegment, ISinglePriceSegment } from "@/interfaces/Routes";
import ResultRouteView from "@/components/ResultRouteView.vue";
import RoutesSVG from "@/components/RoutesSVG.vue";
import { revalidateRoutes } from "@/services/calculator";

const props = withDefaults(defineProps<{
    routes: ICalculatorExtendedResult,
    editable?: boolean,
}>(), { editable: false });

const buildErrorMessage = (
    val: number,
    multiService: boolean,
    routeIndex: number,
    segmentIndex: number,
    priceIndex?: number,
) => (
    `Can not set price ${val} to ${multiService ? "multi" : "one"}-service route `
    + `with route index = ${routeIndex}, segment index = ${segmentIndex}`
    + (priceIndex === undefined ? "" : ` and price index = ${priceIndex}`)
    + ": element is undefined"
);

function updateSinglePrice(
    val: number,
    segmentIndex: number,
    routeIndex: number,
    multiService: boolean,
) {
    const route = (multiService ? props.routes.multiService : props.routes.oneService)[routeIndex]?.[0];
    if (!route)
        throw new Error(buildErrorMessage(val, multiService, routeIndex, segmentIndex));

    const segment = (route as ISinglePriceSegment[])[segmentIndex];
    if (!segment)
        throw new Error(buildErrorMessage(val, multiService, routeIndex, segmentIndex));

    segment.price = val;
    revalidateRoutes(false);
}

function updateMultiPrice(
    val: number,
    priceIndex: number,
    segmentIndex: number,
    routeIndex: number,
    multiService: boolean,
) {
    const route = (multiService ? props.routes.multiService : props.routes.oneService)[routeIndex]?.[0];
    if (!route)
        throw new Error(buildErrorMessage(val, multiService, routeIndex, segmentIndex, priceIndex));

    const priceVariant = (route as IMultiPriceSegment[])[segmentIndex]?.prices[priceIndex];
    if (!priceVariant)
        throw new Error(buildErrorMessage(val, multiService, routeIndex, segmentIndex, priceIndex));

    priceVariant.value = val;
    revalidateRoutes(false);
}
</script>

<template>
    <div hidden="hidden">
        <RoutesSVG />
    </div>

    <h3>Сквозные маршруты</h3>
    <div id="results-direct" class="mt-4" v-if="routes.oneService.length">
        <ResultRouteView
            v-for="(route, index) in routes.oneService"
            :key="index"
            :route="route"
            :editable="editable"
            @update:single-price="(val: number, segId: number) => updateSinglePrice(val, segId, index, false)"
            @update:multi-price="(val: number, segId: number, routeId: number) => updateMultiPrice(val, segId, routeId, index, false)"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>

    <h3>Прочие маршруты</h3>
    <div id="results-other" class="mt-4" v-if="routes.multiService.length">
        <ResultRouteView
            v-for="(route, index) in routes.multiService"
            :key="index"
            :route="route"
            :editable="editable"
            @update:single-price="(val: number, segId: number) => updateSinglePrice(val, segId, index, true)"
            @update:multi-price="(val: number, segId: number, routeId: number) => updateMultiPrice(val, segId, routeId, index, true)"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>
</template>

<style scoped></style>
