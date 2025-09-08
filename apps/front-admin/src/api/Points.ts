import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { PointAddResponse, PointsAddRequest, PointsGetResponse, PointsSearchResponse } from "../interfaces/Points";


export const pointsService = {
    async search(searchText: string): Promise<PointsSearchResponse> {
        try {
            const response = await axios.post(
                API_ENDPOINTS.POINTS.SEARCH,
                null,
                {
                    params: {
                        search_txt: searchText,
                    },
                    headers: { "Content-Type": "application/json" },
                },
            );

            return response.data;
        } catch (error) {
            console.error("Error searching points:", error);
            throw error;
        }
    },
    async getPoints(): Promise<PointsGetResponse> {
        try {
            const response = await axios.post(
                API_ENDPOINTS.POINTS.GET,
                null,
                {
                    params: {},
                    headers: { "Content-Type": "application/json" },
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
