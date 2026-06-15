import { computed, ref } from "vue";

export type CalculationStatus = "idle" | "loading" | "loading-warnings" | "warnings" | "error" | "completed";

const status = ref<CalculationStatus>("idle");

export function useCalculationStatus() {
    function setStatus(s: CalculationStatus) {
        status.value = s;
    }

    function reset() {
        status.value = "idle";
    }

    return { status: computed(() => status.value), setStatus, reset };
}
