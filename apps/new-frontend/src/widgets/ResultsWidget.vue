<script setup lang="ts">
import type { ICalculatorResult } from "@/interfaces/APIResponses";
import ResultRouteView from "@/components/ResultRouteView.vue";
import RoutesSVG from "@/components/RoutesSVG.vue";

defineProps<{
    routes: ICalculatorResult,
}>();
</script>

<template>
    <div hidden="hidden">
        <RoutesSVG />
    </div>

    <h3>Сквозные маршруты</h3>
    <div id="results-direct" class="mt-4" v-if="routes.one_service_routes.length">
        <ResultRouteView
            v-for="route in routes.one_service_routes"
            :key="JSON.stringify(route)"
            :route="route"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>

    <h3>Прочие маршруты</h3>
    <div id="results-other" class="mt-4" v-if="routes.multi_service_routes.length">
        <ResultRouteView
            v-for="route in routes.multi_service_routes"
            :key="JSON.stringify(route)"
            :route="route"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>
</template>

<style scoped></style>
