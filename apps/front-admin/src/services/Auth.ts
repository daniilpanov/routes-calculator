import router from "@/router";
import { LOGIN_CHECK_INTERVAL, ROUTES } from "@/constants";
import * as AuthAPI from "@/api/Auth";
import { ILoginCredentials } from "@/interfaces/Auth";

let updateUserInfoIntervalId: number | undefined;

async function updateUserInfo() {
    try {
        const response = await AuthAPI.me();
        if (getUserName() !== response.username)
            localStorage.setItem("username", response.username);
    } catch (e) {
        await logout();
    }
}

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

        if (updateUserInfoIntervalId === undefined)
            updateUserInfoIntervalId = window.setInterval(updateUserInfo, LOGIN_CHECK_INTERVAL);

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
        await router.navigate(ROUTES.LOGIN);

        if (updateUserInfoIntervalId !== undefined) {
            clearInterval(updateUserInfoIntervalId);
            updateUserInfoIntervalId = undefined;
        }
    }
}

export const getUserName = () => localStorage.getItem("username") || null;

export const isAuth = () => !!getUserName();
