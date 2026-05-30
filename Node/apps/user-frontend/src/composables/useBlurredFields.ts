import { useFeatureFlags } from "@/stores/featureFlags";
import { computed } from "vue";

export function useBlurredFields() {
    const blurredFields = computed(() => useFeatureFlags().blurredFields);

    const isFieldBlurred = (field: string) => blurredFields.value.includes(field);

    return { blurredFields, isFieldBlurred };
}
