<script setup lang="ts">
import SelectWithFilter from "@/components/SelectWithFilter.vue";

import { computed, watch } from "vue";
import { useRates } from "@/stores/rates";

const { rates, currentRate, setCurrentRate } = useRates();

const selectedCurrencyModel = defineModel<string | undefined>({
    required: false,
    default: undefined,
});
selectedCurrencyModel.value = currentRate;

const pinnedCurrencies = ["RUB", "USD", "EUR", "CNY"];
const pinnedCurrenciesOptions = computed(() =>
    pinnedCurrencies.map((currency: string) => ({ value: currency, label: currency }))
);

const ratesOptions = computed(() => {
    if (!rates) return [];

    const currencies = Object.keys(rates).filter(
        (currency: string) => !pinnedCurrencies.includes(currency)
    );
    const ratesOptions = new Array(currencies.length);
    for (const i in currencies) ratesOptions[i] = { value: currencies[i], label: currencies[i] };

    return ratesOptions;
});

watch(selectedCurrencyModel, (currency: string | undefined) =>
    currency ? setCurrentRate(currency) : undefined
);
</script>

<template>
    <SelectWithFilter
        v-model="selectedCurrencyModel"
        :options="ratesOptions"
        :pinned-options="pinnedCurrenciesOptions"
        label="Выберите валюту"
        required
    />
</template>
