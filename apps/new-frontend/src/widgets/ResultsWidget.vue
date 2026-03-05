<script setup lang="ts">
import type { ICalculatorExtendedResult } from "@/interfaces/Routes";
import ResultRouteView from "@/components/ResultRouteView.vue";
import RoutesSVG from "@/components/RoutesSVG.vue";

defineProps<{
    routes: ICalculatorExtendedResult,
}>();
</script>

<template>
    <div hidden="hidden">
        <RoutesSVG />
    </div>

    <h3>Сквозные маршруты</h3>
    <div id="results-direct" class="mt-4" v-if="routes.oneService.length">
        <ResultRouteView
            v-for="route in routes.oneService"
            :key="JSON.stringify(route)"
            :route="route"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>

    <h3>Прочие маршруты</h3>
    <div id="results-other" class="mt-4" v-if="routes.multiService.length">
        <ResultRouteView
            v-for="route in routes.multiService"
            :key="JSON.stringify(route)"
            :route="route"
        />
    </div>
    <div v-else>
        <h5>Не найдены</h5>
    </div>
</template>

<style scoped></style>
