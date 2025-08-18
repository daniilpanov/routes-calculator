import axios from "axios";
import { BASE_API_URL, API_ENDPOINTS } from "./ApiConfig";

interface LoginData {
    login: string;
    password: string;
}

/*interface LoginResponse {
  status: "OK"
}*/

export const authService = {
    async login(credentials: LoginData) {
        try {
            const response = await axios.post(
                BASE_API_URL + API_ENDPOINTS.AUTH.LOGIN
                ,
                credentials,
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Login failed");
        }
    },
};
