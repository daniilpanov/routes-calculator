<script setup lang="ts">
import type { IPoint, IdIsExternal } from "@/interfaces/Point";
import PointsSelect from "@/widgets/PointsSelect.vue";

import { getDepartures, getDestinations } from "@/api_helpers/points";
import { onMounted, ref, useId, watch } from "vue";

const dateModel = defineModel<string>("date");
const showAllRoutesModel = defineModel<boolean>("showAllRoutes");
const departureIdsModel = defineModel<IdIsExternal[]>("departure");
const destinationIdsModel = defineModel<IdIsExternal[]>("destination");
const containerTypeModel = defineModel<string>("containerType");
const containerWeightModel = defineModel<number>("containerWeight");

const departureInputDisabledModel = defineModel<boolean>("isDepartureDisabled", { required: false, default: true });
const destinationInputDisabledModel = defineModel<boolean>("isDestinationDisabled", { required: false, default: true });

const departureInputTextModel = defineModel<string>("departureSearchText", { required: false, default: "" });
const destinationInputTextModel = defineModel<string>("destinationSearchText", { required: false, default: "" });

const emit = defineEmits(["calculate", "reset"]);

const dateInputId = useId();
const containerTypeSelectId = useId();
const containerWeightInputId = useId();

const departurePoints = ref<IPoint[]>([]);
const destinationPoints = ref<IPoint[]>([]);
const calcForm = ref<HTMLFormElement>();

function submit(e: Event) {
    if (!calcForm.value!.checkValidity()) return;

    e.preventDefault();
    emit("calculate");
}

function setSelectedPoints(
    points: typeof departurePoints | typeof destinationPoints,
    idsModel: typeof departureIdsModel | typeof destinationIdsModel,
) {
    if (!idsModel.value?.length)
        return;

    let pointFound: IPoint | undefined;
    for (const selectedId of idsModel.value) {
        for (const point of points.value) {
            if (
                !selectedId.isExternal && point.ids.includes(selectedId.id as number) ||
                selectedId.isExternal && point.external_ids.includes(selectedId.id as string)
            ) {
                pointFound = point;
                break;
            }

            for (const port of point.ports) {
                if (
                    !selectedId.isExternal && port.ids.includes(selectedId.id as number) ||
                    selectedId.isExternal && port.external_ids.includes(selectedId.id as string)
                ) {
                    pointFound = point;
                    break;
                }
            }
            if (pointFound) break;
        }
        if (pointFound) break;
    }

    if (!pointFound) {
        idsModel.value = undefined;
        return;
    }

    let allIds = [
        ...pointFound.ids.map(id => ({ id, isExternal: false })),
        ...pointFound.external_ids.map(id => ({ id, isExternal: true })),
    ];

    for (const port of pointFound.ports)
        allIds = [
            ...port.ids.map(id => ({ id, isExternal: false })),
            ...port.external_ids.map(id => ({ id, isExternal: true })),
        ];

    idsModel.value = allIds.length ? allIds : undefined;
}

const isDateValid = () => (dateModel.value && !isNaN(new Date(dateModel.value).getDay()));

// Update departures on 'dateModel' changing
watch(dateModel, async () => {
    destinationInputDisabledModel.value = true;
    departureInputDisabledModel.value = true;
    departureIdsModel.value = [];
    destinationIdsModel.value = [];

    if (!isDateValid()) return;

    const response = await getDepartures(dateModel.value!);

    const { data } = response;
    departureInputDisabledModel.value = !data.length;
    if (departureInputDisabledModel.value) return;

    departurePoints.value = data;
});

// Update destinations on 'dateModel' or 'selectedDepartures' changing
watch([dateModel, departureIdsModel], async () => {
    destinationInputDisabledModel.value = true;
    destinationIdsModel.value = [];
    destinationPoints.value = [];

    if (!isDateValid() || !departureIdsModel.value) return;

    const response = await getDestinations(dateModel.value!, departureIdsModel.value);

    const { data } = response;
    destinationInputDisabledModel.value = false;
    if (destinationInputDisabledModel.value) return;

    destinationPoints.value = data;
});

// If points is changed then try to set selected point based on the last value
watch(departurePoints, () => {
    if (isDateValid())
        setSelectedPoints(
            departurePoints,
            departureIdsModel,
        );
    else {
        departureIdsModel.value = undefined;
        departureInputDisabledModel.value = true;
    }
});
watch([departurePoints, departureIdsModel, destinationPoints], () => {
    if (!departurePoints.value?.length)
        return;

    if (departureIdsModel.value?.length && isDateValid())
        setSelectedPoints(
            destinationPoints,
            destinationIdsModel,
        );
    else {
        destinationIdsModel.value = undefined;
        destinationInputDisabledModel.value = true;
    }
});

onMounted(async () => {
    if (!isDateValid()) return;

    // Block before loading
    departureInputDisabledModel.value = true;
    destinationInputDisabledModel.value = true;
    // Save initial values
    const initialDepartureIds = departureIdsModel.value;
    const initialDestinationIds = destinationIdsModel.value;

    const depResponse = await getDepartures(dateModel.value!);
    departurePoints.value = depResponse.data;
    departureInputDisabledModel.value = false;

    // Restore selected departure if it is in URL
    if (initialDepartureIds && departurePoints.value.length)
        setSelectedPoints(departurePoints, departureIdsModel);
    else departureIdsModel.value = undefined;

    // Load destinations if a departure is selected
    if (departureIdsModel.value) {
        const destResponse = await getDestinations(dateModel.value!, departureIdsModel.value);
        destinationPoints.value = destResponse.data;
        destinationInputDisabledModel.value = false;

        // Restore selected destination if it is in URL
        if (initialDestinationIds && destinationPoints.value.length) {
            // Rewrite model because 'watch' erases it
            destinationIdsModel.value = initialDestinationIds;
            setSelectedPoints(destinationPoints, destinationIdsModel);
        } else destinationIdsModel.value = undefined;
    } else {
        destinationPoints.value = [];
        destinationIdsModel.value = undefined;
        destinationInputDisabledModel.value = true;
    }
});
</script>

<template>
    <form ref="calcForm">
        <div class="mb-3">
            <label :for="dateInputId" class="form-label">Дата отгрузки</label>
            <input
                type="date"
                class="form-control"
                :id="dateInputId"
                v-model="dateModel"
                value=""
                required
            />
        </div>

        <div class="mb-3">
            <label>
                <input type="checkbox" v-model="showAllRoutesModel" />
                Показать устаревшие маршруты
            </label>
        </div>

        <div class="mb-3 position-relative">
            <PointsSelect
                :points="departurePoints"
                text-label="Пункт отправки"
                v-model="departureIdsModel"
                v-model:is-disabled="departureInputDisabledModel"
                v-model:search-text="departureInputTextModel"
            />
        </div>

        <div class="mb-3 position-relative">
            <PointsSelect
                :points="destinationPoints"
                text-label="Пункт отправки"
                v-model="destinationIdsModel"
                v-model:is-disabled="destinationInputDisabledModel"
                v-model:search-text="destinationInputTextModel"
            />
        </div>

        <div class="mb-3">
            <label :for="containerTypeSelectId" class="form-label">Тип контейнера</label>
            <select
                class="form-select"
                :id="containerTypeSelectId"
                v-model="containerTypeModel"
                required
            >
                <option selected disabled value="">Выберите тип контейнера</option>
                <option value="20">20'DC</option>
                <option value="40">40'HC</option>
            </select>
        </div>

        <div class="md-3 row">
            <div class="col-md">
                <label :for="containerWeightInputId" class="form-label">Вес груза (т)</label>
                <input
                    type="number"
                    class="form-control"
                    :id="containerWeightInputId"
                    v-model="containerWeightModel"
                    min="1"
                    step="1"
                    max="28"
                    placeholder="Введите вес груза"
                    required
                />
            </div>
        </div>

        <p></p>
        <hr />

        <div class="md-3 row">
            <button type="submit" @click.stop="submit" class="btn btn-primary col-md">
                Расcчитать
            </button>
            <button type="reset" @click.stop="$emit('reset')" class="btn btn-danger col-md">Очистить</button>
        </div>
    </form>
</template>
