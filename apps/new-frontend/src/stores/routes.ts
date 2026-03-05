import type { ICalculatorExtendedResult } from "@/interfaces/Routes";

import { defineStore } from "pinia";
import { ref } from "vue";

export const useRoutes = defineStore("routes", () => {
    const routes = ref<ICalculatorExtendedResult | undefined>();

    const setRoutes = (newRoutes?: ICalculatorExtendedResult) => (routes.value = newRoutes);

    return { routes, setRoutes };
});
