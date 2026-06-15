<script setup lang="ts">
import { computed } from "vue";
import { useCalculationStatus } from "@/composables/useCalculationStatus";

const { status } = useCalculationStatus();

const color = computed(() => {
    switch (status.value) {
        case "loading":
        case "loading-warnings":
        case "warnings":
            return "#fd7e14";
        case "error":
            return "#dc3545";
        case "completed":
            return "#198754";
        default:
            return "#6c757d";
    }
});

const isSpinning = computed(() => status.value === "loading" || status.value === "loading-warnings");

const showExclamation = computed(() => status.value === "loading-warnings" || status.value === "warnings" || status.value === "error");

const showIcon = computed(() => status.value !== "idle");

const tooltipText = computed(() => {
    switch (status.value) {
        case "loading":
            return "Просчёт маршрутов...";
        case "loading-warnings":
            return "Просчёт маршрутов (есть предупреждения)...";
        case "warnings":
            return "Просчёт завершён с предупреждениями";
        case "error":
            return "Ошибка просчёта маршрутов";
        case "completed":
            return "Просчёт маршрутов завершён";
        default:
            return "";
    }
});
</script>

<template>
    <div
        v-if="showIcon"
        class="calculation-status-indicator"
        :class="{ spinning: isSpinning }"
        :title="tooltipText"
        role="status"
        :style="{ borderColor: color }"
    >
        <svg
            viewBox="0 0 16 16"
            :style="{ color: color }"
        >
            <template v-if="isSpinning && !showExclamation">
                <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="28" stroke-dashoffset="10" />
            </template>
            <template v-else>
                <circle cx="8" cy="8" r="7" fill="var(--bs-body-bg, white)" stroke="currentColor" stroke-width="1.5" />
                <path v-if="showExclamation" d="M8 4.5a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5zm0 6.5a.6.6 0 1 1 0-1.2.6.6 0 0 1 0 1.2z" fill="currentColor" />
                <path v-else-if="status==='completed'" d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z" fill="currentColor" />
            </template>
        </svg>
    </div>
</template>

<style scoped>
.calculation-status-indicator {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    width: 2.5rem;
    height: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--bs-body-bg, white);
    border: 2px solid transparent;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    z-index: 9999;
    cursor: default;
    transition: border-color 0.3s;

    & > svg {
        width: 1.5rem;
        height: 1.5rem;
    }
}

.calculation-status-indicator.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
