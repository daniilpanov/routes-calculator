import { API_ENDPOINTS } from "./ApiConfig";
import { ILoginCredentials } from "@/interfaces/Auth";
import ExecuteProtectedRequest from "@/services/ExecuteProtectedRequest";
import axios, { AxiosError } from "axios";

interface ILoginResponse {
    status: string;
}

interface IMeResponse {
    username: string;
}

export async function login(credentials: ILoginCredentials): Promise<ILoginResponse> {
    try {
        const response = await axios.post<ILoginResponse>(
            `${API_ENDPOINTS.AUTH.LOGIN}`,
            credentials,
            {
                headers: {
                    "Content-Type": "application/json",
                },
                withCredentials: true,
            },
        );
        return response.data;
    } catch (e) {
        const error = e as AxiosError;
        if (error.response?.status === 401)
            throw new Error("Unauthorized");

        throw new Error("Unexpected error during login");
    }
}

export async function logout() {
    return await axios.delete<ILoginResponse> (
        `${API_ENDPOINTS.AUTH.LOGOUT}`,
        {
            withCredentials : true,
        },
    );
}

export async function refresh(): Promise<ILoginResponse> {
    try {
        const response = await axios.post<ILoginResponse>(
            `${API_ENDPOINTS.AUTH.REFRESH}`,
            {
                withCredentials : true,
            },
        );
        return response.data;
    } catch (error) {
        throw new Error("Unexpected error during refresh");
    }
}

export async function me(): Promise<IMeResponse> {
    const response = await ExecuteProtectedRequest<IMeResponse>(
        async () => axios.get<IMeResponse>(
            `${API_ENDPOINTS.AUTH.ME}`,
            {
                withCredentials : true,
            },
        ),
    );

    return response.data;
}
