import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { getContainersResponse } from "@/interfaces/Response/ContainersResponse";


export const containersApi = {
    async getContainers(): Promise<getContainersResponse> {
        try {
            const response = await axios.get<getContainersResponse>(
                API_ENDPOINTS.CONTAINERS.GET,
            );
            return response.data;
        } catch (error: any) {
            console.log("Error:", error.response?.data || error.message);
            throw error;
        }
    },
};
