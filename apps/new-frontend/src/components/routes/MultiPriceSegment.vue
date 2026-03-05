<script setup lang="ts">
import type { IMultiPriceSegment } from "@/interfaces/Routes";
import RouteTypeIcon from "@/components/RouteTypeIcon.vue";
import OnePriceInMultiSegment from "@/components/routes/OnePriceInMultiSegment.vue";

withDefaults(defineProps<{
    segment: IMultiPriceSegment,
    editable?: boolean,
}>(), { editable: false });

defineEmits(["update:price"]);
</script>

<template>
    <div class="align-items-center my-2 result-segment">
        <div>
            <RouteTypeIcon :type="segment.type" />
            {{ segment.company }}
        </div>
        <div class="mb-2">
            Ставка действует:
            {{ new Date(segment.effectiveFrom).toLocaleDateString() }}
            —
            {{ new Date(segment.effectiveTo).toLocaleDateString() }}
        </div>

        <div class="mb-3">
            <div class="row">
                <OnePriceInMultiSegment
                    class="col-md"
                    :price-variant="price"
                    :key="JSON.stringify(price)"
                    :editable="editable"
                    v-for="(price, index) in segment.prices"
                    @update:price="(val: number) => $emit('update:price', [val, index])"
                />
            </div>
        </div>
        <div>
            <div>
                <strong>{{ segment.startPointCountry.toUpperCase() }}, {{ segment.startPointName }}</strong>
                →
                <strong>{{ segment.endPointCountry.toUpperCase() }}, {{ segment.endPointName }}</strong>
            </div>
        </div>

        <blockquote v-if="segment.comment">
            <p>Комментарий: <i>{{ segment.comment }}</i></p>
        </blockquote>
    </div>
</template>

<style scoped>
.result-segment strong {
    white-space: nowrap;
}
</style>
