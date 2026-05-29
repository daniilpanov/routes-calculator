import { defineStore } from "pinia";
import { ref } from "vue";

export const useFeatureFlags = defineStore("featureFlags", () => {
    const blurredFields = ref<string[]>([]);

    const setBlurredFields = (fields: string[]) => {
        blurredFields.value = fields;
    };

    const clearBlurredFields = () => {
        blurredFields.value = [];
    };

    return { blurredFields, setBlurredFields, clearBlurredFields };
});
