import { Drop } from "@/interfaces/Model/Drop";

export interface getDropsResponse {
    status: string,
    count: number
    drops: Drop[],
}
export interface addDropResponse{
    status: string,
    new_drop: Drop
}


