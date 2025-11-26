import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { PointAddResponse, PointsAddRequest } from "@/interfaces/Points";
import { PointsGetResponse, searchPointsResponse } from "@/interfaces/Response/PointsResponse";
import { PointsGetRequest } from "@/interfaces/Request/Points";


export const pointsApi = {
    async searchPoints(
        searchText: string,
    ): Promise<searchPointsResponse> {
        try {
            const response = await axios.get<searchPointsResponse>(
                `/admin/api/points/${searchText}`,
                {
                    params: { search_txt: searchText },
                },
            );
            return response.data;
        } catch (error: any) {
            console.log("Error:", error.response?.data || error.message);
            throw error;
        }
    },
    async getPoints(data: PointsGetRequest): Promise<PointsGetResponse> {
        try {
            const response = await axios.post<PointsGetResponse>(
                API_ENDPOINTS.POINTS.GET,
                data,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error getting points:", error);
            throw error;
        }
    },
    async addPoints(data: PointsAddRequest): Promise<PointAddResponse> {
        try {
            const response = await axios.post(
                API_ENDPOINTS.POINTS.ADD,
                data,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error adding points:", error);
            throw error;
        }
    },
};
