<script setup lang="ts">
import type { ICompany } from "@/interfaces/Company";

import SelectWithFilter from "@/components/SelectWithFilter.vue";

import { useLang } from "@/stores/lang";
import { usePoints } from "@/stores/points";
import { computed } from "vue";

interface Props {
    pointIds: (string | number)[];
    textLabel: string;
}

const props = defineProps<Props>();
const selectedPointModel = defineModel<string | number>({ required: false, default: undefined });

const { lang } = useLang();
const { pointsIndexedById } = usePoints();

const pointOptions = computed(() =>
    props.pointIds.map((pointId: string | number) => {
        const point = pointsIndexedById.get(pointId);
        if (!point) throw new Error(`Point with ID ${pointId} is undefined`);

        const companiesString = point.companies.map((company: ICompany) => company.name).join(",");

        const translate = point.translates.get(lang);
        if (!translate) throw new Error(`Translation for point ${pointId} not found`);

        const pointName = translate.name + translate.country;
        const label = companiesString ? `${pointName}[${companiesString}]` : pointName;

        return { value: pointId, label };
    })
);
</script>

<template>
    <SelectWithFilter
        v-model="selectedPointModel"
        :options="pointOptions"
        :label="textLabel"
        :placeholder="textLabel"
        required
    />
</template>
