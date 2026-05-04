import CalculatorPage from "@/pages/CalculatorPage.vue";
import LoginPage from "@/pages/LoginPage.vue";

import { deserializeCalculatorQueryParams } from "@/services/calculator";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/login",
            name: "login",
            component: LoginPage,
        },
        {
            path: "/",
            name: "calculator",
            component: CalculatorPage,
            props: (route: { query: Record<string, unknown> }) => deserializeCalculatorQueryParams(route.query),
        },
    ],
});

export default router;
