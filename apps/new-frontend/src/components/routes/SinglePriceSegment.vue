<script setup lang="ts">
import type { ISinglePriceSegment } from "@/interfaces/Routes";

import RouteTypeIcon from "@/components/RouteTypeIcon.vue";
import PriceWithCurrency from "@/components/PriceWithCurrency.vue";

defineProps<{
    segment: ISinglePriceSegment,
}>();

defineEmits(["update:price"]);
</script>

<template>
    <div class="align-items-center my-2 result-segment">
        <div>
            <RouteTypeIcon :type="segment.type" />
            {{ segment.company }}
        </div>
        <div class="mb-2">
            <span v-if="segment.beginCond">Условия: {{ segment.beginCond }} - {{ segment.finishCond }}</span>
            <span v-else>&emsp;</span>
        </div>
        <div class="mb-2">Ставка действует: {{ new Date(segment.effectiveFrom).toLocaleDateString() }} — {{ new Date(segment.effectiveTo).toLocaleDateString() }}</div>
        <div class="mb-3">Контейнер: {{ segment.container.name }}</div>
        <div>
            <div>
                <strong>{{ segment.startPointCountry.toUpperCase() }}, {{ segment.startPointName }}</strong>
                →
                <strong>{{ segment.endPointCountry.toUpperCase() }}, {{ segment.endPointName }}</strong>
            </div>
            <div>
                <PriceWithCurrency
                    :price="segment.price"
                    :currency="segment.currency"
                    @update:price="(val: number) => $emit('update:price', val)"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.result-segment strong {
    white-space: nowrap;
}
</style>
