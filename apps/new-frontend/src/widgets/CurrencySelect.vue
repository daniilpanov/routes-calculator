<script setup lang="ts">
import SelectWithFilter from "@/components/SelectWithFilter.vue";
import { computed, watch } from "vue";

import type { RatesMap } from "@/stores/rates";

const props = defineProps<{ rates: RatesMap }>();
const selectedCurrencyModel = defineModel<string | undefined>({
    required: false,
    default: undefined,
});

const pinnedCurrencies = ["RUB", "USD", "EUR", "CNY"];
const pinnedOptions = computed(() =>
    pinnedCurrencies.map((currency: string) => ({ value: currency, label: currency }))
);

const ratesOptions = computed((): { value: string; label: string }[] => {
    if (!props.rates.size) return [];

    const currencies = [...props.rates.keys()].filter(
        (currency: string) => !pinnedCurrencies.includes(currency)
    );

    const ratesOptions: { value: string; label: string }[] = Array.from({ length: currencies.length });
    for (const i in currencies) ratesOptions[i] = { value: currencies[i]!, label: currencies[i]! };

    return ratesOptions;
});

watch(selectedCurrencyModel, (currency?: string) =>
    currency ? (selectedCurrencyModel.value = currency) : undefined
);
</script>

<template>
    <SelectWithFilter
        v-model="selectedCurrencyModel"
        :options="ratesOptions"
        :pinned-options="pinnedOptions"
        label="Выберите валюту"
        required
    />
</template>
