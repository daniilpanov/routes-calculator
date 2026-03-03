<script setup lang="ts">
import { getCurrencySymbol } from "@/helpers/currency";
import { roundPrice } from "@/helpers/roundPrice";
import { computed } from "vue";

const props = defineProps<{
    price: number,
    currency: string,
}>();

const currencySymbol = computed(
    () => getCurrencySymbol(props.currency)
);

const numberFormatter = new Intl.NumberFormat();
const fp = (price: number) => numberFormatter.format(price)
</script>

<template>
    <span v-if="currencySymbol">
        {{ currencySymbol }}
    </span>

    <span>{{ fp(roundPrice(price)) }}</span>

    <template v-if="!currencySymbol">
        &nbsp;
        {{ currency }}
    </template>
</template>
