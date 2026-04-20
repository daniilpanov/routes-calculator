<script setup lang="ts">
import type { IService } from "@/interfaces/Service";

defineProps<{
    service: IService;
}>();
</script>

<template>
    <div class="row">
        <div class="col-md-8">
            <div>{{ service.name }}</div>
            <small v-if="service.description" class="text-muted">{{ service.description }}</small>
        </div>
        <div class="col-md-4 text-end">
            <span>{{ service.price }} {{ service.currency }}</span>
        </div>
    </div>
</template>
