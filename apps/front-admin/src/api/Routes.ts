import { api } from "./api";
import { API_ENDPOINTS } from "./ApiConfig";
import {
    CreateRouteResponse,
    DeleteRouteResponse,
    GetRoutesResponse,
    RouteCreateRequest,
    RouteDeleteRequest,
    RouteEditRequest,
    RouteEditResponse,
} from "../interfaces/Routes";

export const routesService = {
    async getRoutes(
        page = 1,
        limit = 25,
        filter_fields: Record<string, string | number> = {},
    ): Promise<GetRoutesResponse> {
        const response = await api.post<GetRoutesResponse>(
            API_ENDPOINTS.ROUTES.GET,
            { page, limit, filter_fields },
        );
        return response.data;
    },

    async deleteRoute(data: RouteDeleteRequest): Promise<DeleteRouteResponse> {
        const response = await api.delete<DeleteRouteResponse>(
            API_ENDPOINTS.ROUTES.DELETE,
            { data },
        );
        return response.data;
    },

    async createRoute(data: RouteCreateRequest): Promise<CreateRouteResponse> {
        const response = await api.post<CreateRouteResponse>(
            API_ENDPOINTS.ROUTES.CREATE,
            data,
        );
        return response.data;
    },

    async editRoute(data: RouteEditRequest): Promise<RouteEditResponse> {
        const response = await api.put<RouteEditResponse>(
            API_ENDPOINTS.ROUTES.EDIT,
            data,
        );
        return response.data;
    },
};
