import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { DeleteRouteResponse, GetRoutesResponse } from "../interfaces/Routes";



export const routesService = {
    async getRoutes(page = 1, limit = 25): Promise<GetRoutesResponse> {
        try {
            const response = await axios.post<GetRoutesResponse>(
                API_ENDPOINTS.ROUTES.GET,
                { page, limit, filter_fields: {} },
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during getRoutes");
        }
    },

    async deleteRoute(id: number): Promise<DeleteRouteResponse> {
        try {
            const response = await axios.delete<DeleteRouteResponse>(
                `${API_ENDPOINTS.ROUTES.DELETE}?route_id=${id}`,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during deleteRoute");
        }
    },
    async createRoute(): Promise<any> {
        try {
            const response = await axios.post<GetRoutesResponse>(
                API_ENDPOINTS.ROUTES.CREATE,
                null,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            );
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during createRoute");
        }
    },
};
