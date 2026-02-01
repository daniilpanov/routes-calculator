<script setup lang="ts">
import { ref, onMounted, watch } from "vue";

interface Props {
    options: unknown[];
    tabindex?: number;
}

const props = withDefaults(defineProps<Props>(), {
    tabindex: 0,
});

const emit = defineEmits<{
    (e: "input", value: unknown): void;
}>();

const selected = ref(props.options.length > 0 ? props.options[0] : null);
const open = ref(false);

onMounted(() => {
    emit("input", selected.value);
});

watch(
    () => props.options,
    (newOptions) => {
        if (newOptions.length > 0 && !selected.value) {
            selected.value = newOptions[0];
            emit("input", selected.value);
        }
    },
    { immediate: true }
);
</script>

<template>
    <div class="custom-select" :tabindex="tabindex" @blur="open = false">
        <div class="selected" :class="{ open: open }" @click="open = !open">
            {{ selected }}
        </div>
        <div class="items" :class="{ selectHide: !open }">
            <div
                class="item"
                v-for="(option, i) of options"
                :key="i"
                @click="
                    selected = option;
                    open = false;
                    $emit('input', option);
                "
            >
                {{ option }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-select {
    position: relative;
    width: 100%;
    text-align: left;
    outline: none;
    height: 47px;
    line-height: 47px;
}

.selected {
    background-color: #080d0e;
    border-radius: 6px;
    border: 1px solid #858586;
    color: #ffffff;
    padding-left: 8px;
    cursor: pointer;
    user-select: none;
}

.selected.open {
    border: 1px solid #ce9b2c;
    border-radius: 6px 6px 0 0;
}

.selected:after {
    position: absolute;
    content: "";
    top: 22px;
    right: 10px;
    width: 0;
    height: 0;
    border-radius: 4px;
    border-style: solid;
    border-color: #fff transparent transparent transparent;
}

.items {
    color: #ffffff;
    border-radius: 0 0 6px 6px;
    overflow: hidden;
    border-right: 1px solid #ce9b2c;
    border-left: 1px solid #ce9b2c;
    border-bottom: 1px solid #ce9b2c;
    position: absolute;
    background-color: #080d0e;
    left: 0;
    right: 0;
}

.item {
    color: #ffffff;
    padding-left: 8px;
    cursor: pointer;
    user-select: none;
}

.item:hover {
    background-color: #b68a28;
}

.selectHide {
    display: none;
}
</style>
