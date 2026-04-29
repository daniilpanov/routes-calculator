import { defineStore } from "pinia";
import { ref } from "vue";

import type { IUser } from "@/interfaces/User";

export const useUser = defineStore("user", () => {
    const user = ref<IUser | null>(null);
    const setUser = (newUser: IUser) => (user.value = newUser);
    const removeUser = () => (user.value = null);
    const isAuth = () => !!user.value;

    return { user, setUser, removeUser, isAuth };
});
