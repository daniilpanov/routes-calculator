import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import {
    CreateRouteResponse,
    DeleteRouteResponse,
    GetRoutesResponse,
    RouteCreateRequest,
    RouteDeleteRequest,
    RouteEditRequest,
    RouteEditResponse,
} from "@/interfaces/Routes";

export const routesApi = {
    async getRoutes(
        page = 1,
        limit = 25,
        filter_fields: Record<string, string | number> = {},
    ): Promise<GetRoutesResponse> {
        try {
            const response = await axios.get<GetRoutesResponse>(
                API_ENDPOINTS.ROUTES.GET,
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

    async deleteRoute(data: RouteDeleteRequest): Promise<DeleteRouteResponse> {
        const response = await axios.delete<DeleteRouteResponse>(
            API_ENDPOINTS.ROUTES.DELETE,
            { data },
        );
        return response.data;
    },

    async createRoute(data: RouteCreateRequest): Promise<CreateRouteResponse> {
        const response = await axios.post<CreateRouteResponse>(
            API_ENDPOINTS.ROUTES.CREATE,
            data,
        );
        return response.data;
    },

    async editRoute(data: RouteEditRequest): Promise<RouteEditResponse> {
        const response = await axios.put<RouteEditResponse>(
            API_ENDPOINTS.ROUTES.EDIT,
            data,
        );
        return response.data;
    },
};
