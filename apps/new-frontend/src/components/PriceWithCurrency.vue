<script setup lang="ts">
import { getCurrencySymbol } from "@/helpers/currency";
import { roundPrice } from "@/helpers/roundPrice";
import { computed, ref, watch } from "vue";

const props = withDefaults(defineProps<{
    price: number,
    currency: string,
    editable?: boolean,
}>(), { editable: false });

const currencySymbol = computed(
    () => getCurrencySymbol(props.currency)
);

defineEmits(["update:price"]);

const priceRef = ref<number>(props.price);

const numberFormatter = new Intl.NumberFormat();
const fp = (price: number) => numberFormatter.format(price);

watch(() => props.price, (newPrice: number) => (priceRef.value = newPrice));
</script>

<template>
    <span v-if="currencySymbol">
        {{ currencySymbol }}
    </span>

    <input v-if="editable" v-model="priceRef" @blur="$emit('update:price', priceRef)" type="number">
    <span v-else>{{ fp(roundPrice(price)) }}</span>

    <template v-if="!currencySymbol">
        &nbsp;
        {{ currency }}
    </template>
</template>
