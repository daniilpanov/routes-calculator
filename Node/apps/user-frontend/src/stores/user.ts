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

export const useUserUpdateIntervalId = defineStore("userUpdateIntervalId", () => {
    const intervalId = ref<number | undefined>();
    const setIntervalId = (newId: number) => (intervalId.value = newId);
    const removeIntervalId = () => (intervalId.value = undefined);

    return { intervalId, setIntervalId, removeIntervalId };
});

export const useUserUpdateIntervalInMinutes = defineStore("userUpdateIntervalInMinutes", () => {
    const initialValue = localStorage.getItem("userUpdateIntervalInMinutes");
    let parsedInitialValue = undefined;
    if (initialValue)
        parsedInitialValue = Number.parseInt(initialValue);

    const interval = ref<number | undefined>(parsedInitialValue);
    const setInterval = (newInterval: number) => {
        interval.value = newInterval;
        localStorage.setItem("userUpdateIntervalInMinutes", String(newInterval));
    };
    const removeInterval = () => {
        interval.value = undefined;
        localStorage.removeItem("userUpdateIntervalInMinutes");
    };

    return { interval, setInterval, removeInterval };
});
