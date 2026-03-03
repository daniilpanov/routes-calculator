import type { ICalculatorResult } from "@/interfaces/APIResponses";

import { defineStore } from "pinia";
import { ref } from "vue";

export const useRoutes = defineStore("routes", () => {
    const routes = ref<ICalculatorResult | undefined>();

    const setRoutes = (newRoutes?: ICalculatorResult) => (routes.value = newRoutes);

    return { routes, setRoutes };
});
