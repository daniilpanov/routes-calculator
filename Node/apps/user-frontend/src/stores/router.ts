import { defineStore } from "pinia";
import { ref, toRaw } from "vue";

import type { Router } from "vue-router";

export const useRouter = defineStore("router", () => {
    const router = ref<Router>();

    const setRouter = (newRouter: Router) => (router.value = newRouter);

    const getCurrentRoute = () => toRaw(router.value)?.currentRoute;

    return { router, setRouter, getCurrentRoute };
});
