<script setup lang="ts">
import BeautifulRatio from "@/components/BeautifulRatio.vue";
import type { IService } from "@/interfaces/Service";

import { inject, ref, watch } from "vue";
import type { Ref } from "vue";

const props = defineProps<{
    service: IService;
}>();

const emit = defineEmits(["update:checked"]);
const checked = ref<boolean>(props.service.checked);
const printMode: Ref<boolean> = inject("printMode") || ref(false);

watch(checked, (val: boolean) => emit("update:checked", val));
</script>

<template>
    <div class="row">
        <div class="col-md-1 print-mode--hidden">
            <BeautifulRatio :is-disabled="service.mandatory" v-model="checked" />
        </div>
        <div :class="{'col-md-6': !printMode, 'col-md-7': printMode}">
            <div>{{ service.name }}</div>
            <small v-if="service.description" class="text-muted">{{ service.description }}</small>
        </div>
        <div :class="{'col-md-4': !printMode, 'col-md-5': printMode}" class="text-end">
            <span>{{ service.price }} {{ service.currency }}</span>
        </div>
    </div>
</template>
