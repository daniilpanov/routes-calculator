import { ILoginCredentials } from "@/interfaces/Auth";
import * as AuthAPI from "@/api/Auth";
import { ROUTES } from "@/constants";
import router from "@/router";

async function updateUserInfo() {
    try {
        await refresh();

        const response = await AuthAPI.me();
        if (getUserName() !== response.username)
            localStorage.setItem("username", response.username);
    } catch (e) {
        await logout();
    }
}

function startUserInfoUpdateInterval(interval: number) {
    const intervalId = localStorage.getItem("userInfoUpdateIntervalId");
    if (intervalId)
        return false;

    localStorage.setItem("userInfoUpdateIntervalId", String(setInterval(updateUserInfo, interval)));
    localStorage.setItem("userInfoUpdateInterval", String(interval));
    return true;
}

function stopUserInfoUpdateIntervalId() {
    const intervalId = localStorage.getItem("userInfoUpdateIntervalId");
    if (!intervalId)
        return false;

    clearInterval(Number(intervalId));
    localStorage.removeItem("userInfoUpdateIntervalId");
    return true;
}

export const onStartup = () =>
    updateUserInfo().then(() => {
        stopUserInfoUpdateIntervalId();

        const interval = localStorage.getItem("userInfoUpdateInterval");
        if (!interval)
            return;

        startUserInfoUpdateInterval(Number(interval));
    });

export async function refresh() {
    try {
        const response = await AuthAPI.refresh();
        if (response.status !== "OK")
            await logout();
    } catch (e) {
        console.error(e);
        await logout();
    }
}

export async function login(credentials: ILoginCredentials) {
    try {
        const response = await AuthAPI.login(credentials);

        if (response.status !== "OK")
            return false;

        await updateUserInfo();

        if (response.accessTokenExpiredIn)
            startUserInfoUpdateInterval(Math.floor(response.accessTokenExpiredIn * 60 * 1000 / 2));

        return true;
    } catch (e) {
        const error = e as Error;
        if (error.message === "Unauthorized")
            return false;

        throw e;
    }
}

export async function logout() {
    try {
        await AuthAPI.logout();
    } catch (e) {
        /** @suppress no-empty due to we don't need to log this error */
    } finally {
        localStorage.removeItem("username");
        stopUserInfoUpdateIntervalId();

        await router.navigate(ROUTES.LOGIN);
    }
}

export const getUserName = () => localStorage.getItem("username") || null;

export const isAuth = () => !!getUserName();
