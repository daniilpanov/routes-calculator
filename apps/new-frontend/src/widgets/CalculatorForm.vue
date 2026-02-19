<script setup lang="ts">
import PointsSelect from "@/widgets/PointsSelect.vue";
import { ref, useId } from "vue";

const dateModel = defineModel<string>("date");
const showAllRoutesModel = defineModel<boolean>("showAllRoutes");
const departureIdModel = defineModel<string | number>("departure");
const destinationIdModel = defineModel<string | number>("destination");
const containerTypeModel = defineModel<number>("containerType");
const containerWeightModel = defineModel<number>("containerWeight");

const emit = defineEmits(["calculate", "reset"]);

const dateInputId = useId();
const containerTypeSelectId = useId();
const containerWeightInputId = useId();

const departurePointIds = ref<number[]>([1, 2]);
const destinationPointIds = ref<number[]>([1, 2]);
const calcForm = ref<HTMLFormElement>();

function submit(e: Event) {
    if (!calcForm.value!.checkValidity()) return;

    e.preventDefault();
    emit("calculate");
}
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
                :point-ids="departurePointIds"
                text-label="Пункт отправки"
                v-model="departureIdModel"
            />
        </div>

        <div class="mb-3 position-relative">
            <PointsSelect
                :point-ids="destinationPointIds"
                text-label="Пункт отправки"
                v-model="destinationIdModel"
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
                Расcчитать!
            </button>
            <button type="reset" @click.stop="$emit('reset')" class="btn col-md">Clear</button>
        </div>
    </form>
</template>

<style scoped></style>
