import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { ContainersResponse } from "@/interfaces/Containers";


export const containersService = {
    async getContainers(): Promise<ContainersResponse> {
        try {
            const response = await axios.post(
                API_ENDPOINTS.CONTAINERS.GET,
                undefined,
                {
                    headers: { "Content-Type": "application/json" },
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error searching points:", error);
            throw error;
        }
    },
};
