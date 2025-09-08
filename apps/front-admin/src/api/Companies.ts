import { GetRoutesResponse } from "../interfaces/Routes";
import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { Company } from "../interfaces/Companies";

export interface GetCompaniesResponse {
    status: string,
    companies: Company[],
}

export const companiesService = {
    async getCompanies(): Promise<GetCompaniesResponse> {
        try {
            const response = await axios.post<GetCompaniesResponse>(
                API_ENDPOINTS.COMPANIES.GET,
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
};
