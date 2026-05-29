<script setup lang="ts">
withDefaults(defineProps<{
    text?: string;
}>(), {
    text: "████████",
});
</script>

<template>
    <span class="blurred-text" aria-hidden="true">{{ text }}</span>
</template>

<style scoped>
.blurred-text {
    display: inline-block;
    max-width: 100%;
    filter: blur(5px);
    user-select: none;
    pointer-events: none;
    opacity: 0.85;
}
</style>
