import axios from "axios";
import { API_ENDPOINTS } from "./ApiConfig";
import { PointsSearchResponse } from "../interfaces/Points";

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
};
