<script setup lang="ts">
import type { ModelRef } from "@vue/runtime-core";

import CurrencySelect from "@/widgets/CurrencySelect.vue";
import CalculatorForm from "@/widgets/CalculatorForm.vue";
import { useRates } from "@/stores/rates";
import { useRouter } from "vue-router";
import { ref } from "vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";

interface Props {
    date?: string;
    showAllRoutes?: boolean;
    departureId?: string | number;
    destinationId?: string | number;
    containerType?: number;
    containerWeight?: number;
    currency?: string;
}

const data = defineProps<Props>();

const { setCurrentRate } = useRates();
const router = useRouter();

if (data.currency) setCurrentRate(data.currency);

let allParamsSent = false;
for (const item of Object.values(data))
    if (item === undefined) {
        allParamsSent = false;
        break;
    }

console.log(data, allParamsSent);

const dateModel = defineModel<string | undefined>("date");
if (!dateModel.value) dateModel.value = new Date().toLocaleDateString("en-CA");

const showAllRoutesModel = defineModel<boolean>("showAllRoutes");
const departureIdModel = defineModel<string | number>("departure");
const destinationIdModel = defineModel<string | number>("destination");
const containerTypeModel = defineModel<number>("containerType");
const containerWeightModel = defineModel<number>("containerWeight");

const loading = ref(false);

const models: { [key: string]: ModelRef<unknown> } = {
    date: dateModel,
    showAllRoutes: showAllRoutesModel,
    departureId: departureIdModel,
    destinationId: destinationIdModel,
    containerType: containerTypeModel,
    containerWeight: containerWeightModel,
};

for (const [key, val] of Object.entries(data)) {
    if (val === undefined) continue;

    if (models[key]) models[key].value = val;
}

function calculate() {
    const { currentRate } = useRates();
    router.push({
        query: {
            date: dateModel.value,
            showAllRoutes: showAllRoutesModel.value ? "true" : "false",
            departureId: departureIdModel.value,
            destinationId: destinationIdModel.value,
            type: containerTypeModel.value,
            weight: containerWeightModel.value,
            currency: currentRate,
        },
    });
    loading.value = true;
}

function reset() {
    router.push({ query: {} });
    loading.value = false;
}
</script>

<template>
    <div class="my-5">
        <div class="card shadow-sm rounded-4 p-4">
            <h2 class="mb-4 text-center">Калькулятор маршрутов</h2>

            <CalculatorForm
                v-model:date="dateModel"
                v-model:departure="departureIdModel"
                v-model:destination="destinationIdModel"
                v-model:show-all-routes="showAllRoutesModel"
                v-model:container-type="containerTypeModel"
                v-model:container-weight="containerWeightModel"
                @calculate="calculate"
                @reset="reset"
            />
        </div>

        <hr />
        <h3>Просуммировать стоимость маршрутов в валюте:</h3>
        <div class="mb-3 position-relative">
            <CurrencySelect />
        </div>
    </div>

    <hr />

    <div class="results">
        <LoadingSpinner v-if="loading" />
    </div>
</template>

<style scoped></style>
