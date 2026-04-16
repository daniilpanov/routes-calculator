<script setup lang="ts">
import { RouteType } from "@/interfaces/Routes";

defineProps<{
    type: string,
}>();
</script>

<template>
    <span>
        <template v-if="type.toUpperCase() === RouteType.SEA_RAIL">
            <svg
                class="flex-shrink-0"
                width="24"
                height="24"
                role="img"
            >
                <use xlink:href="#SEA" />
            </svg>
            +
            <svg
                class="flex-shrink-0 me-2"
                width="24"
                height="24"
                role="img"
            >
                <use xlink:href="#RAIL" />
            </svg>
        </template>
        <svg
            v-else
            class="flex-shrink-0 me-2"
            width="24"
            height="24"
            role="img"
        >
            <use :xlink:href="'#' + type.toUpperCase()" />
        </svg>
    </span>
</template>

<style scoped>

</style>
