<script setup lang="ts">
import type { IService } from "@/interfaces/Service";
import type { Ref } from "vue";

import ServiceView from "@/components/ServiceView.vue";
import { inject, ref, computed } from "vue";

const props = defineProps<{
    services: IService[];
}>();

defineEmits(["update:checked"]);

const printMode: Ref<boolean> = inject("printMode") || ref(false);
const isExpanded = ref<boolean>(false);

const shouldShowContent = computed(() => printMode.value || isExpanded.value);

const filteredServices = computed(
    ()  => printMode.value
        ? props.services.filter((item: IService) => item.checked)
        : props.services
);
</script>

<template>
    <div class="services-container border rounded p-3 mt-3" v-show="filteredServices.length">
        <button
            v-if="!printMode"
            @click="isExpanded = !isExpanded"
            class="btn btn-link p-0 mb-2"
        >
            {{ isExpanded ? "Свернуть список услуг" : "Развернуть список услуг" }}
        </button>

        <div v-if="shouldShowContent">
            <div v-for="(service, index) in filteredServices" :key="index" class="mb-2">
                <ServiceView :service="service" @update:checked="(val: boolean) => $emit('update:checked', val, index)" />
            </div>
        </div>
    </div>
</template>
