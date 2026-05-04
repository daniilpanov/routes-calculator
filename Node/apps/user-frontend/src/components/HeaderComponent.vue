<script setup lang="ts">
import { computed } from "vue";
import type { RatesMap } from "@/stores/rates";
import { useUser } from "@/stores/user.ts";
import { logout } from "@/services/auth.ts";

const props = defineProps<{ rates: RatesMap }>();

const USD = computed(() => props.rates.get("USD"));
const EUR = computed(() => props.rates.get("EUR"));
const CNY = computed(() => props.rates.get("CNY"));
</script>

<template>
    <nav class="navbar navbar-expand-lg">
        <div class="container">
            <a class="navbar-brand" href="#">Калькулятор</a>

            <button class="btn btn-outline-danger" v-if="useUser().isAuth()" @click.stop="logout()">
                Выйти
            </button>

            <div class="collapse navbar-collapse" id="navbarNavAltMarkup"></div>
            <div class="navbar-nav"></div>

            <div class="header-rates">
                <div v-if="USD">
                    <span class="symbol">$</span> {{ USD }}
                </div>
                <div v-if="EUR">
                    <span class="symbol">€</span> {{ EUR }}
                </div>
                <div v-if="CNY">
                    <span class="symbol">¥</span> {{ CNY }}
                </div>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.header-rates .symbol {
    font-size: larger;
    color: var(--bs-blue);
}
</style>
