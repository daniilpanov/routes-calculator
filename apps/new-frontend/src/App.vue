<script setup lang="ts">
import type { ITranslatePoint } from "@/interfaces/Point";

import { useRates } from "@/stores/rates";
import { usePoints } from "@/stores/points";

const { setRates, setCurrentRate } = useRates();
const { setPoints } = usePoints();

setPoints([
    {
        id: 1,
        translates: new Map<string, ITranslatePoint>([
            [
                "ru",
                {
                    entityId: 1,
                    lang: "ru",
                    country: "test1",
                    name: "test1",
                },
            ],
        ]),
        ports: [],
        companies: [{ id: 123, name: "tetetet" }],
    },
    {
        id: 2,
        translates: new Map<string, ITranslatePoint>([
            [
                "ru",
                {
                    entityId: 2,
                    lang: "ru",
                    country: "test2",
                    name: "test2",
                },
            ],
        ]),
        ports: [],
        companies: [],
    },
    {
        id: 3,
        translates: new Map<string, ITranslatePoint>([
            [
                "ru",
                {
                    entityId: 3,
                    lang: "ru",
                    country: "test3",
                    name: "test3",
                },
            ],
        ]),
        ports: [],
        companies: [],
    },
]);

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
