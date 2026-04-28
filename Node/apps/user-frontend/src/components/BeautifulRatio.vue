<script setup lang="ts">
withDefaults(defineProps<{
    isDisabled?: boolean,
}>(), {
    isDisabled: false,
});

const checked = defineModel<boolean>();
</script>

<template>
    <label class="beautiful-switcher-wrapper">
        <input class="beautiful-switcher" type="checkbox" role="switch" v-model="checked" :disabled="isDisabled" />
    </label>
</template>

<style scoped>
.beautiful-switcher-wrapper {
    display: flex;
}

.beautiful-switcher {
    --thumb-size: 1.5rem;
    --track-size: 3rem;
    --track-padding: 0.25rem;
    --track-bg-inactive: var(--bs-gray-500);
    --track-bg-active: var(--bs-green);
    --thumb-position: 0%;

    appearance: none;
    box-sizing: content-box;
    cursor: pointer;
    user-select: none;
    -webkit-tap-highlight-color: transparent;

    inline-size: var(--track-size);
    block-size: var(--thumb-size);
    padding: var(--track-padding);
    border-radius: var(--track-size);
    background-color: var(--track-bg-inactive);

    flex-shrink: 0;
    display: grid;
    align-items: center;
    grid: [track] 1fr / [track] 1fr;
}

.beautiful-switcher::before {
    content: "";
    grid-area: track;
    inline-size: var(--thumb-size);
    block-size: var(--thumb-size);

    border-radius: 50%;
    background-color: var(--bs-light);
    box-shadow: 0 0 1rem var(--bs-green);
    border: 1px solid var(--bs-gray-500);

    transition: transform 0.75s ease, background-color 0.75s ease;
    transform: translateX(var(--thumb-position));
}

.beautiful-switcher:checked {
    --thumb-position: calc(var(--track-size) - 100%);
    background-color: var(--track-bg-active);
}

.beautiful-switcher:indeterminate {
    --thumb-position: calc(var(--track-size) / 2 - var(--thumb-size) / 2);
}

.beautiful-switcher:disabled {
    opacity: 0.5;
    cursor: auto;
}
</style>
