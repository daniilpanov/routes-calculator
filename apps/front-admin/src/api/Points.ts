import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { PointAddResponse, PointsAddRequest, PointsSearchResponse } from "@/interfaces/Points";
import { PointsGetResponse } from "@/interfaces/Response/Points";
import { PointsGetRequest } from "@/interfaces/Request/Points";


export const pointsService = {
    async search(searchText: string): Promise<PointsSearchResponse> {
        try {
            const response = await axios.post(
                API_ENDPOINTS.POINTS.SEARCH,
                undefined,
                {
                    params: { search_txt: searchText },
                    headers: { "Content-Type": "application/json" },
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error searching points:", error);
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
