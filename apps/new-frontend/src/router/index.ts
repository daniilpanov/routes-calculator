import CalculatorPage from "@/pages/CalculatorPage.vue";

import { createRouter, createWebHistory } from "vue-router";

const parseCalculatorQueryParams = (query: Record<string, unknown>) => {
    const params: Record<string, unknown> = {};

    if (query.currency) params.currency = query.currency;

    if (query.date && !Number.isNaN(new Date(query.date as string).getDate()))
        params.date = query.date;

    if (query.showAllRoutes) params.showAllRoutes = query.showAllRoutes === "true";

    if (query.departureId) {
        const num = Number(query.departureId);
        params.departureId = isNaN(num) ? query.departureId : num;

        if (query.destinationId) {
            const num = Number(query.destinationId);
            params.destinationId = isNaN(num) ? query.destinationId : num;
        }
    }

    if (query.type) params.containerType = Number(query.type);

    if (query.weight) params.containerWeight = Number(query.weight);

    return params;
};

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "calculator",
            component: CalculatorPage,
            props: (route) => parseCalculatorQueryParams(route.query),
        },
    ],
});

export default router;
