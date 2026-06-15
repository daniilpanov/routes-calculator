import { ref } from "vue";

export interface Toast {
    id: number;
    message: string;
    type: "error" | "success" | "warning";
}

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useToast() {
    function show(message: string, type: Toast["type"] = "error", durationMs: number = 5000) {
        const id = nextId++;
        toasts.value.push({ id, message, type });

        setTimeout(() => {
            toasts.value = toasts.value.filter((t) => t.id !== id);
        }, durationMs);
    }

    function dismiss(id: number) {
        toasts.value = toasts.value.filter((t) => t.id !== id);
    }

    return { toasts, show, dismiss };
}