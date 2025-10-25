import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { Company } from "@/interfaces/Companies";
import request from "@/services/ExecuteProtectedRequest";

export interface GetCompaniesResponse {
    status: string,
    companies: Company[],
}

export const companiesService = {
    async getCompanies(): Promise<GetCompaniesResponse> {
        try {
            const response = await request<GetCompaniesResponse>(() => axios.post(
                API_ENDPOINTS.COMPANIES.GET,
                undefined,
                {
                    headers: { "Content-Type": "application/json" },
                    withCredentials: true,
                },
            ));
            return response.data;
        } catch (error) {
            throw new Error("Unexpected error during getRoutes");
        }
    },
};
