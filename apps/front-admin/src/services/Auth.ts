import { ILoginCredentials } from "@/interfaces/Auth";
import * as AuthAPI from "@/api/Auth";
import { LOGIN_CHECK_INTERVAL, ROUTES } from "@/constants";
import router from "@/router";

const loginCheckTimeout = setInterval(updateUserInfo, LOGIN_CHECK_INTERVAL);

async function updateUserInfo() {
    try {
        const response = await AuthAPI.me();
        if (!response.username)
            return await refresh();

        if (getUserName() !== response.username)
            localStorage.setItem("username", response.username);
    } catch (e) {
        await refresh();
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
    } finally {
        localStorage.removeItem("username");
        await router.navigate(ROUTES.LOGIN);
    }
}

export const getUserName = () => localStorage.getItem("username") || null;

export const isAuth = () => !!getUserName();
