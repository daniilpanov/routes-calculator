import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { getCompaniesResponse } from "@/interfaces/Response/CompaniesResponse";
import { getCompaniesRequest } from "@/interfaces/Request/CompaniesRequest";


export const companiesService = {
    async getCompanies(
        page = 1,
        limit = 25,
    ): Promise<getCompaniesResponse> {
        try {
            const params: getCompaniesRequest = {
                page,
                limit,
            };
            const response = await axios.get<getCompaniesResponse>(
                API_ENDPOINTS.COMPANIES.GET,
                {
                    params: {
                        params,
                    },
                },
            );
            return response.data;
        } catch (error: any) {
            console.log("Error:", error.response?.data || error.message);
            throw error;
        }
    },
};
