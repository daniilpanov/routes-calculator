import CalculatorPage from "@/pages/CalculatorPage.vue";
import Error404Page from "@/pages/Error404Page.vue";
import LoginPage from "@/pages/LoginPage.vue";

import { deserializeCalculatorQueryParams } from "@/services/calculator";
import { useDemoAuth } from "@/stores/demoAuth.ts";
import { createRouter, createWebHistory } from "vue-router";

import type { RouteLocationNormalizedGeneric } from "vue-router";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/login",
            name: "login",
            component: LoginPage,
        },
        {
            path: "/demo/:uid",
            name: "demo",
            component: CalculatorPage,
            props: (route: { query: Record<string, unknown> }) => deserializeCalculatorQueryParams(route.query),
            beforeEnter: async (to: RouteLocationNormalizedGeneric) => {
                const uid = to.params.uid as string;
                if (uid)
                    useDemoAuth().setDemo(uid);
                else {
                    useDemoAuth().clearDemo();
                    return { name: "404", params: { pathMatch: ["demo"] } };
                }

                try {
                    const res = await fetch("/api/v2/demo/validate", {
                        method: "POST",
                        headers: { "X-Demo-User-UID": uid },
                    });
                    if (!res.ok)
                        return { name: "404", params: { pathMatch: to.path.substring(1).split("/") } };
                } catch (e) {
                    console.log(e);
                    return { name: "404", params: { pathMatch: to.path.substring(1).split("/") } };
                }
            },
        },
        {
            path: "/",
            name: "calculator",
            component: CalculatorPage,
            props: (route: { query: Record<string, unknown> }) => deserializeCalculatorQueryParams(route.query),
        },
        {
            path: "/:pathMatch(.*)*",
            name: "404",
            component: Error404Page,
        },
    ],
});

export default router;
