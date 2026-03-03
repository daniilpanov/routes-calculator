<script setup lang="ts">
import type { IMultiPriceSegment, ISinglePriceSegment, RouteDescriptor } from "@/interfaces/Routes";

import MultiPriceSegment from "@/components/routes/MultiPriceSegment.vue";
import SinglePriceSegment from "@/components/routes/SinglePriceSegment.vue";
import PriceWithCurrency from "@/components/PriceWithCurrency.vue";

import { computed } from "vue";

const props = defineProps<{
    route: RouteDescriptor,
}>();

const segments = computed(
    () => props.route[0]
);
const drop = computed(
    () => props.route[1]
);
</script>

<template>
    <div class="p-3 mb-4 border rounded shadow-sm result-item">
        <div v-if="props.route[2]" class="alert alert-warning d-flex align-items-center" role="alert">
            <svg class="flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Warning:"><use xlink:href="#exclamation-triangle-fill"/></svg>
            <div>
                Маршрут может быть неактуален
            </div>
        </div>

        <div class="segments row">
            <div class="segment col-md m-2" :key="JSON.stringify(segment)" v-for="(segment, i) in segments">
                <div class="row">
                    <div class="col-md-11">
                        <SinglePriceSegment :segment="segment as ISinglePriceSegment" v-if="(segment as ISinglePriceSegment).price" />
                        <MultiPriceSegment :segment="segment as IMultiPriceSegment" v-else />
                    </div>
                    <div class="col-md-1 segments-divider" v-if="i < segments.length - 1">
                        <span class="d-md-inline">&rightarrow;</span>
                        <span class="d-md-none">&downarrow;</span>
                    </div>
                </div>
            </div>
        </div>

        <hr>

        <div class="drop-off row">
            <div class="col-md-7">Drop off:</div>
            <div class="col-md-5">
                <span v-if="drop?.price">
                    <b><PriceWithCurrency :price="drop.price" :currency="drop.currency" /></b>
                    <span v-if="drop.conversation_percents" class="text-muted drop-off-conversation">
                        + {{ drop.conversation_percents }}% конвертация в рубли
                    </span>
                </span>
                <b v-else>включен</b>
            </div>
        </div>
    </div>
</template>

<style scoped>
.segments-divider {
    font-size: xx-large;

    display: flex;
    align-items: center;

    & > .d-md-inline {
        display: none;
    }
}
</style>
