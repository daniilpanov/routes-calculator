import type { RouteExtendedDescriptor } from "@/interfaces/Routes";

import { defineStore } from "pinia";
import { ref } from "vue";

export const useRoutes = defineStore("routes", () => {
    const routes = ref<RouteExtendedDescriptor[] | undefined>();

    const setRoutes = (newRoutes?: RouteExtendedDescriptor[]) => (routes.value = newRoutes);

    return { routes, setRoutes };
});
