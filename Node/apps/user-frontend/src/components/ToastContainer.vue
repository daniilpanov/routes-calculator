<script setup lang="ts">
import { useToast } from "@/composables/useToast";

const { toasts, dismiss } = useToast();
</script>

<template>
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1080;">
        <TransitionGroup name="toast">
            <div
                v-for="toast in toasts"
                :key="toast.id"
                :class="['toast show d-flex align-items-center', `text-bg-${toast.type}`]"
                role="alert"
            >
                <div class="toast-body">
                    {{ toast.message }}
                </div>
                <button
                    type="button"
                    class="btn-close btn-close-white me-2 m-auto"
                    @click="dismiss(toast.id)"
                ></button>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
    transition: all 0.3s ease;
}

.toast-enter-from {
    opacity: 0;
    transform: translateX(100%);
}

.toast-leave-to {
    opacity: 0;
    transform: translateX(100%);
}
</style>