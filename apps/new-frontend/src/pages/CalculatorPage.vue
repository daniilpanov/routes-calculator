<script setup lang="ts">
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import CalculatorForm from "@/widgets/CalculatorForm.vue";
import CurrencySelect from "@/widgets/CurrencySelect.vue";
import ResultsWidget from "@/widgets/ResultsWidget.vue";

import { clearRoutes, revalidateRoutes, serializeCalculatorQueryParams } from "@/services/calculator";
import { updateRoutes } from "@/services/calculator";
import { useRates } from "@/stores/rates";
import { useRoutes } from "@/stores/routes";

import { useRouter } from "vue-router";
import { computed, nextTick, onMounted, ref } from "vue";

import type { IdIsExternal } from "@/interfaces/Point";
import type { RatesMap } from "@/stores/rates";
import type { ICalculatorExtendedResult } from "@/interfaces/Routes";
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
        if (locker) locker.then(() => {
            ratesStore.setCurrentRate(val);
            revalidateRoutes();
        });
        else ratesStore.setCurrentRate(val);
    },
});

const routesStore = useRoutes();
const routesRef = computed((): ICalculatorExtendedResult | undefined => routesStore.routes);

const editMode = ref<boolean>(false);

const router = useRouter();

const resultsElementRef = ref<HTMLElement | undefined>();

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

async function calculate(pushURL: boolean = true) {
    loading.value = true;

    await nextTick();
    resultsElementRef.value?.scrollIntoView({ behavior: "smooth" });

    await ratesStore.getLocker();

    if (pushURL)
        await router.push({
            query: serializeCalculatorQueryParams({
                date: dateModel.value,
                showAllRoutes: showAllRoutesModel.value,
                departureIds: departureIdsModel.value,
                destinationIds: destinationIdsModel.value,
                containerType: containerTypeModel.value,
                containerWeight: containerWeightModel.value,
                currency: ratesStore.currentRate,
            }),
        });

    await updateRoutes({
        date: dateModel.value,
        showAllRoutes: showAllRoutesModel.value,
        departureIds: departureIdsModel.value,
        destinationIds: destinationIdsModel.value,
        containerType: containerTypeModel.value,
        containerWeight: containerWeightModel.value,
    });

    loading.value = false;

    await nextTick();
    resultsElementRef.value?.scrollIntoView({ behavior: "smooth" });
}

function reset() {
    router.push({ query: {} });
    currentRateRef.value = "RUB";
    loading.value = false;
    departureIdsModel.value = undefined;
    destinationIdsModel.value = undefined;
    clearRoutes();
}

onMounted(() => {
    currentRateRef.value = props.currency ?? "RUB";

    const data = [
        props.date,
        props.showAllRoutes,
        props.departureIds,
        props.destinationIds,
        props.containerType,
        props.containerWeight,
        props.currency,
    ];
    let allParamsSent = true;
    for (const item of data)
        if (item === undefined) {
            allParamsSent = false;
            break;
        }

    if (allParamsSent) nextTick().then(() => calculate(false));
});
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
                @calculate="calculate"
                @reset="reset"
            />
        </div>

        <hr />
        <h3>Просуммировать стоимость маршрутов в валюте:</h3>
        <div class="mb-3 position-relative">
            <CurrencySelect :rates="ratesRef" v-model="currentRateRef" />
        </div>

        <button class="btn btn-secondary" @click="editMode = !editMode">
            <template v-if="editMode">
                Сохранить и выйти в обычный режим
            </template>
            <template v-else>
                Отредактировать стоимость для КП
            </template>
        </button>
    </div>

    <hr />

    <div ref="resultsElementRef" class="results" v-if="loading || routesRef">
        <div class="text-center" v-if="loading"><LoadingSpinner /></div>
        <ResultsWidget v-else :routes="routesRef!" :editable="editMode" />
    </div>
</template>

<style scoped>
.results {
    min-height: 80vh;
}
</style>
