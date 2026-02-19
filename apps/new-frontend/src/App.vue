<script setup lang="ts">
import { useRates } from "@/stores/rates";
import { updateAllPoints } from "@/services/points";
import { onBeforeMount } from "vue";

const { setRates, setCurrentRate } = useRates();

onBeforeMount(async () => updateAllPoints());

setRates({
    RUB: 1,
    USD: 2,
    EUR: 3,
    CNY: 1,
    AUD: 6,
    BUG: 1321,
});
setCurrentRate("RUB");
</script>

<template>
    <main class="container">
        <div class="alert alert-warning d-flex align-items-center" role="alert">
            <svg
                class="bi flex-shrink-0 me-2"
                width="24"
                height="24"
                role="img"
                aria-label="Warning:"
            >
                <use xlink:href="#exclamation-triangle-fill"></use>
            </svg>
            <div>
                Сервис находится на стадии бета-тестирования. Некоторые функции могут работать
                нестабильно. Пожалуйста, сообщите нам, если заметите ошибку.
            </div>
        </div>

        <router-view />
    </main>
</template>

<style scoped></style>
