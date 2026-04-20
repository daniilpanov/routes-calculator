<script setup lang="ts">
import type { IService } from "@/interfaces/Service";
import type { Ref } from "vue";

import ServiceView from "@/components/ServiceView.vue";
import { inject, ref, computed } from "vue";

defineProps<{
    services: IService[];
}>();

const printMode: Ref<boolean> = inject("printMode") || ref(false);
const isExpanded = ref<boolean>(false);

const shouldShowContent = computed(() => printMode.value || isExpanded.value);
</script>

<template>
    <div class="services-container border rounded p-3 mt-3">
        <button
            v-if="!printMode"
            @click="isExpanded = !isExpanded"
            class="btn btn-link p-0 mb-2"
        >
            {{ isExpanded ? "Свернуть список услуг" : "Развернуть список услуг" }}
        </button>

        <div v-if="shouldShowContent">
            <div v-for="(service, index) in services" :key="index" class="mb-2">
                <ServiceView :service="service" />
            </div>
        </div>
    </div>
</template>
