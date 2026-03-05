<script setup lang="ts">
import { Theme } from "@/services/theme";

const themeModel = defineModel<Theme>({ default: Theme.DARK });
</script>

<template>
    <div class="theme-switcher">
        <input type="radio" name="theme" id="light" v-model="themeModel" :value="Theme.LIGHT" :checked="themeModel === Theme.LIGHT">
        <label for="light" aria-label="Светлая тема">☀️</label>

        <input type="radio" name="theme" id="dark" v-model="themeModel" :value="Theme.DARK" :checked="themeModel === Theme.DARK">
        <label for="dark" aria-label="Тёмная тема">🌙</label>
    </div>
</template>

<style scoped>
.theme-switcher {
    --accent-light: #fbbf24;
    --accent-dark: #3b82f6;
    --switch-bg: #e2e8f0;

    position: fixed;
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    z-index: 999;
}

.theme-switcher input[type="radio"] {
    display: none;
}

.theme-switcher label {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: var(--switch-bg);
    font-size: 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border: 2px solid transparent;
}

.theme-switcher label:hover {
    transform: scale(1.1);
    filter: brightness(0.95);
}

#light:checked ~ label[for="light"] {
    background: var(--accent-light);
    border-color: white;
    box-shadow: 0 0 15px var(--accent-light);
    color: #0f172a;
}

#dark:checked ~ label[for="dark"] {
    background: var(--accent-dark);
    border-color: white;
    box-shadow: 0 0 15px var(--accent-dark);
    color: white;
}
</style>
