<script setup lang="ts">
import { onMounted, ref, useId, watch } from "vue";
import { Modal } from "bootstrap";

interface Props {
    id?: string;
    show?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    id: undefined,
    show: false,
});

const id = ref<string>(props.id ?? useId());
let modalController: Modal;

onMounted(() => (modalController = new Modal(document.getElementById(id.value)!)));

watch(
    () => props.show,
    (newShowValue: boolean) => {
        if (!modalController) return;

        if (newShowValue) modalController.show();
        else modalController.hide();
    },
    { immediate: true }
);
</script>

<template>
    <div class="modal" :id="id" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <slot name="header"></slot>
                    <button
                        type="button"
                        class="btn-close"
                        data-bs-dismiss="modal"
                        aria-label="Close"
                    ></button>
                </div>
                <div class="modal-body">
                    <slot></slot>
                </div>
                <div class="modal-footer">
                    <slot name="footer"></slot>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped></style>
