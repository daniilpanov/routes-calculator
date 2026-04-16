import { ILoginCredentials } from "@/interfaces/Auth";

interface ILoginResponse {
    status: string;
}

interface IMeResponse {
    username: string;
}

export async function login(credentials: ILoginCredentials): Promise<ILoginResponse> {
    return { status: "OK" };
}

export async function logout() {
}

export async function refresh(): Promise<ILoginResponse> {
    return { status: "OK" };
}

export async function me(): Promise<IMeResponse> {
    return { username: "ADMIN" };
}
