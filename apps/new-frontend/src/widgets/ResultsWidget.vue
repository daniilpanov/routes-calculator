<script setup lang="ts">
import type {
    ICalculatorExtendedResult,
    IMultiPriceSegment,
    ISinglePriceSegment,
    RouteExtendedDescriptor
} from "@/interfaces/Routes";

import ResultRouteView from "@/components/ResultRouteView.vue";
import RoutesSVG from "@/components/RoutesSVG.vue";

import { revalidateRoutes } from "@/services/calculator";
import { computed, inject, provide, ref, watch } from "vue";

import type { Ref } from "vue";

const props = defineProps<{
    routes: ICalculatorExtendedResult,
}>();

const editMode: Ref<boolean> = inject("editable") || ref(false);
const printMode: Ref<boolean> = inject("printMode") || ref(false);
const filterSelected = (routes: RouteExtendedDescriptor[]) => routes.filter(r => r[5]);
const filterSelectedIfPrintMode = (routes: RouteExtendedDescriptor[], printMode: boolean) =>
    printMode ? filterSelected(routes) : routes;

const oneService = computed(
    () => filterSelectedIfPrintMode(props.routes.oneService, printMode.value)
);
const multiService = computed(
    () => filterSelectedIfPrintMode(props.routes.multiService, printMode.value)
);

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

const allRoutesSelected = (routes: RouteExtendedDescriptor[]) => {
    for (const route of routes)
        if (!route[5]) return false;

    return true;
}

const areAllRoutesSelected = ref<boolean>(allRoutesSelected(props.routes.oneService) && allRoutesSelected(props.routes.multiService));
const areAllRoutesSelectedSignalRef = ref<boolean>(areAllRoutesSelected.value);
provide("allRoutesSelected", areAllRoutesSelected);
provide("allRoutesSelectedSignal", areAllRoutesSelectedSignalRef);
let quietAllRoutesSelectedChange: boolean = false;

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

function setIsRouteSelected(val: boolean, routeIndex: number, multiService: boolean) {
    if (printMode.value)
        throw new Error("Can not set the route selected in print mode!");

    const route = (multiService ? props.routes.multiService : props.routes.oneService)[routeIndex];
    if (!route)
        throw new Error(`Can not ${val ? "" : "un"}select route with index ${routeIndex}: undefined`);

    route[5] = val;

    if (!val && areAllRoutesSelected.value) {
        quietAllRoutesSelectedChange = true;
        areAllRoutesSelected.value = false;
    } else if (
        val && !areAllRoutesSelected.value
        && allRoutesSelected(props.routes.oneService) && allRoutesSelected(props.routes.multiService)
    ) {
        quietAllRoutesSelectedChange = true;
        areAllRoutesSelected.value = true;
    }
}

watch(areAllRoutesSelected, () => {
    if (quietAllRoutesSelectedChange) quietAllRoutesSelectedChange = false;
    else areAllRoutesSelectedSignalRef.value = !areAllRoutesSelectedSignalRef.value;
});
</script>

<template>
    <div v-show="editMode" class="mb-4">
        <label for="select-all-routes">Добавить все маршруты в КП: </label>
        <input id="select-all-routes" class="m-2" type="checkbox" v-model="areAllRoutesSelected">
    </div>

    <div hidden="hidden">
        <RoutesSVG />
    </div>

    <h3>Сквозные маршруты</h3>
    <div id="results-direct" class="mt-4" v-if="oneService.length">
        <ResultRouteView
            v-for="(route, index) in oneService"
            :key="index"
            :route="route"
            @update:single-price="(val: number, segId: number) => updateSinglePrice(val, segId, index, false)"
            @update:multi-price="(val: number, segId: number, routeId: number) => updateMultiPrice(val, segId, routeId, index, false)"
            @set-selected="(val: boolean) => setIsRouteSelected(val, index, false)"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>

    <h3>Прочие маршруты</h3>
    <div id="results-other" class="mt-4" v-if="multiService.length">
        <ResultRouteView
            v-for="(route, index) in multiService"
            :key="index"
            :route="route"
            @update:single-price="(val: number, segId: number) => updateSinglePrice(val, segId, index, true)"
            @update:multi-price="(val: number, segId: number, routeId: number) => updateMultiPrice(val, segId, routeId, index, true)"
            @set-selected="(val: boolean) => setIsRouteSelected(val, index, true)"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>
</template>

<style scoped></style>
