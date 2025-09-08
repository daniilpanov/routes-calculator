import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { DeleteRouteResponse, GetRoutesResponse, Route } from "../interfaces/Routes";


export interface CreateRouteRequest {
    company: string;
    container: string;
    start_point_name: string;
    end_point_name: string;
    effective_from: string;
    effective_to: string;
    price: {
        [key: string]: number;
    };
}

export interface CreateRouteResponse {
    status: string;
    new_route: Route;
}


export const routesService = {
    async getRoutes(
        page = 1,
        limit = 25,
        filter_fields: Record<string, string | number> = {},
    ): Promise<GetRoutesResponse> {
        try {
            const response = await axios.post<GetRoutesResponse>(
                API_ENDPOINTS.ROUTES.GET,
                { page, limit, filter_fields },
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
    async createRoute(data: CreateRouteRequest): Promise<CreateRouteResponse> {
        try {
            const response = await axios.post<CreateRouteResponse>(
                API_ENDPOINTS.ROUTES.CREATE,
                data,
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
