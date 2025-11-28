import { Drop } from "@/interfaces/Model/Drop";

export interface getDropsResponse {
    status: string,
    count: number
    drops: Drop[],
}


