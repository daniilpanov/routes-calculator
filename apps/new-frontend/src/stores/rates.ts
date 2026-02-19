import { computed, ref } from "vue";
import { defineStore } from "pinia";

export type RatesMap = { [name: string]: number };

export const useRates = defineStore("rates", () => {
    const rates = ref<RatesMap>();
    const currentRate = ref<string>();
    const setRates = (newRates: RatesMap) => (rates.value = newRates);
    const setCurrentRate = (newCurrentRate: string) => {
        if (!rates.value) throw new Error("Rates are not set");

        if (!rates.value[newCurrentRate]) throw new Error(`Undefined rate: "${newCurrentRate}"`);

        currentRate.value = newCurrentRate;
    };

    const currentRateValue = computed(() =>
        rates.value && currentRate.value ? rates.value[currentRate.value] : undefined
    );

    return { rates, currentRate, setRates, setCurrentRate, currentRateValue };
});
