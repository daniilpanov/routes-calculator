<script setup lang="ts">
import CalculatorForm from "@/widgets/CalculatorForm.vue";
import CurrencySelect from "@/widgets/CurrencySelect.vue";

import { useRates } from "@/stores/rates";

import { useRouter } from "vue-router";
import { computed, ref } from "vue";

import type { IdIsExternal } from "@/interfaces/Point";
import type { RatesMap } from "@/stores/rates";
import type { Ref } from "vue";

interface Props {
    date?: string;
    showAllRoutes?: boolean;
    departureIds?: IdIsExternal[];
    destinationIds?: IdIsExternal[];
    containerType?: string;
    containerWeight?: number;
    currency?: string;
}

const props = defineProps<Props>();

const ratesStore = useRates();
const ratesRef = computed((): RatesMap => ratesStore.rates);
const currentRateRef = computed({
    get() { return ratesStore.currentRate; },
    set(val: string) {
        const locker = ratesStore.getLocker();
        if (locker) locker.then(() => ratesStore.setCurrentRate(val));
        else ratesStore.setCurrentRate(val);
    },
});

const router = useRouter();

const dateModel = ref<string | undefined>();
if (!dateModel.value) dateModel.value = new Date().toLocaleDateString("en-CA");

const showAllRoutesModel = ref<boolean>();
const departureIdsModel = ref<IdIsExternal[]>();
const destinationIdsModel = ref<IdIsExternal[]>();
const containerTypeModel = ref<string>();
const containerWeightModel = ref<number>();

const loading = ref(false);

const models: { [key: string]: Ref<unknown> } = {
    date: dateModel,
    showAllRoutes: showAllRoutesModel,
    departureIds: departureIdsModel,
    destinationIds: destinationIdsModel,
    containerType: containerTypeModel,
    containerWeight: containerWeightModel,
};

for (const [key, val] of Object.entries(props)) {
    if (val === undefined) continue;

    if (models[key]) models[key].value = val;
}

function reset() {
    router.push({ query: {} });
    currentRateRef.value = "RUB";
    loading.value = false;
    departureIdsModel.value = undefined;
    destinationIdsModel.value = undefined;
}
</script>

<template>
    <div class="my-5">
        <div class="card shadow-sm rounded-4 p-4">
            <h2 class="mb-4 text-center">Калькулятор маршрутов</h2>

            <CalculatorForm
                v-model:date="dateModel"
                v-model:departure="departureIdsModel"
                v-model:destination="destinationIdsModel"
                v-model:show-all-routes="showAllRoutesModel"
                v-model:container-type="containerTypeModel"
                v-model:container-weight="containerWeightModel"
                @reset="reset"
            />
        </div>

        <hr />
        <h3>Просуммировать стоимость маршрутов в валюте:</h3>
        <div class="mb-3 position-relative">
            <CurrencySelect :rates="ratesRef" v-model="currentRateRef" />
        </div>
    </div>

    <hr />
</template>
