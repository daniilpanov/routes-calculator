import axios from "axios";
import { BASE_API_URL, API_ENDPOINTS } from "./ApiConfig";
import { LoginData, LoginResponse } from "../interfaces/Auth";

export const authService = {
    async login(credentials: LoginData): Promise<LoginResponse> {
        try {
            const response = await axios.post<LoginResponse>(
                `${BASE_API_URL}${API_ENDPOINTS.AUTH.LOGIN}`,
                credentials,
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                    withCredentials: true,
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during login");
        }
    },
    async logout(): Promise<LoginResponse> {
        try {
            const response = await axios.delete<LoginResponse>(
                `${BASE_API_URL}${API_ENDPOINTS.AUTH.LOGOUT}`,
                {
                    withCredentials: true,
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during logout");
        }
    },
};
