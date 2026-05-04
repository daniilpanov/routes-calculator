import * as AuthAPI from "@/api_helpers/user";
import { useUser, useUserUpdateIntervalId, useUserUpdateIntervalInMinutes } from "@/stores/user";

import type { ILoginCredentials } from "@/interfaces/User";

function stopRefreshingInterval() {
    if (!useUserUpdateIntervalId().intervalId)
        return;

    clearInterval(useUserUpdateIntervalId().intervalId);
    useUserUpdateIntervalId().removeIntervalId();
    useUserUpdateIntervalInMinutes().removeInterval();
}

export function setupRefreshingInterval(minutesInterval: number) {
    if (!useUserUpdateIntervalId().intervalId)
        useUserUpdateIntervalId().setIntervalId(setInterval(updateUser, minutesInterval * 60 * 1000));

    useUserUpdateIntervalInMinutes().setInterval(minutesInterval);
}

export async function login(credentials: ILoginCredentials) {
    try {
        const response = await AuthAPI.login(credentials);
        if (response.status !== "OK")
            return false;

        await updateUser();

        if (response.accessTokenExpiredInMinutes)
            setupRefreshingInterval(Math.floor(response.accessTokenExpiredInMinutes / 2));

        return true;
    } catch (e) {
        const error = e as Error;
        if (error.message === "Unauthorized")
            return false;

        throw e;
    }
}

export async function logout() {
    await AuthAPI.logout();
    useUser().removeUser();
    stopRefreshingInterval();
}

export async function updateUser(){
    await AuthAPI.refresh();
    useUser().setUser(await AuthAPI.me());
}
