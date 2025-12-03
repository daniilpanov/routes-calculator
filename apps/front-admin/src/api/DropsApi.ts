import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { addDropResponse, deleteDropResponse, getDropsResponse } from "@/interfaces/Response/DropsResponse";
import { CreateRouteResponse, RouteCreateRequest } from "@/interfaces/Routes";
import { PointAddResponse, PointsAddRequest } from "@/interfaces/Points";
import { addDropRequest, deleteDropRequest, editDropRequest } from "@/interfaces/Request/DropsRequest";

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
    async addDrops(data: addDropRequest): Promise<addDropResponse> {
        try {
            const response = await axios.post<addDropResponse>(
                API_ENDPOINTS.DROPS.ADD,
                data,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error adding drops:", error);
            throw error;
        }
    },
    async deleteDrops(data: { ids: number[] }): Promise<deleteDropResponse> {
        try {
            const response = await axios.delete<deleteDropResponse>(
                API_ENDPOINTS.DROPS.DELETE,
                { data },
            );

            return response.data;
        } catch (error) {
            console.error("Error deleting drop:", error);
            throw error;
        }
    },
    async editDrops(data: editDropRequest){
        try {
            const response = await axios.put(
                `${API_ENDPOINTS.DROPS.DELETE}${data.drop_id}`,
                data,
            );

            return response.data;
        } catch (error) {
            console.error("Error editing drop:", error);
            throw error;
        }
    },
};
