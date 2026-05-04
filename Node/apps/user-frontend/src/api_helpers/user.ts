import type { ILoginResponse } from "@/interfaces/APIResponses";
import type { ILoginCredentials, IUser } from "@/interfaces/User";

export async function login(credentials: ILoginCredentials): Promise<ILoginResponse> {
    const response = await fetch("/api/user/login", {
        body: JSON.stringify(credentials),
        method: "POST",
        headers: { "Content-Type": "application/json" },
    });

    if (response.status === 401)
        throw new Error("Unauthorized");

    if (response.status !== 200)
        throw new Error(`Unexpected error [/api/user/login]: ${response.status} ${response.statusText}`);

    return await response.json() as ILoginResponse;
}

export async function refresh() {
    const response = await fetch("/api/user/token/refresh", { method: "POST" });

    if (response.status === 401)
        throw new Error("Unauthorized");

    if (response.status !== 200)
        throw new Error(`Unexpected error [/api/user/login]: ${response.status} ${response.statusText}`);
}

export const logout = async () =>
    (await fetch("/api/user/logout", { method: "DELETE" })).status === 200;

export async function me(): Promise<IUser> {
    const res = await fetch("/api/user/me");
    if (res.status === 401)
        throw new Error("Unauthorized [/api/user/me]");

    if (res.status !== 200)
        throw new Error(`Unexpected error [/api/user/me]: ${res.status} ${res.statusText}`);

    return await res.json() as IUser;
}
