import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useDemoAuth = defineStore("demoAuth", () => {
    const demoUid = ref<string | null>(null);
    const isDemo = computed(() => !!demoUid.value);

    const setDemo = (uid: string) => {
        demoUid.value = uid;
    };

    const clearDemo = () => {
        demoUid.value = null;
    };

    return { demoUid, isDemo, setDemo, clearDemo };
});
