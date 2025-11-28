import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { getDropsResponse } from "@/interfaces/Response/DropsResponse";

export const dropsApi = {
    async getDrops(
        page = 1,
        limit = 25,
        filter_fields: Record<string, string | number> = {},
    ): Promise<getDropsResponse> {
        try {
            const response = await axios.get<getDropsResponse>(
                API_ENDPOINTS.DROPS.GET,
                {
                    params: {
                        page,
                        limit,
                        ...filter_fields,
                    },
                },
            );
            return response.data;
        } catch (error: any) {
            console.log("Error:", error.response?.data || error.message);
            throw error;
        }
    },
};
