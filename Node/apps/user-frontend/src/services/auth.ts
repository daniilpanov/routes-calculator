import * as AuthAPI from "@/api_helpers/user";
import { useUser } from "@/stores/user";

import type { ILoginCredentials } from "@/interfaces/User";

export async function login(credentials: ILoginCredentials) {
    try {
        const response = await AuthAPI.login(credentials);
        if (response.status !== "OK")
            return false;

        await updateUser();
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
}

export const updateUser = async () => useUser().setUser(await AuthAPI.me());
