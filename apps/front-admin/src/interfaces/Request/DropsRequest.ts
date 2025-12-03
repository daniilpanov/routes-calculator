export interface addDropRequest {
    company_id: number,
    container_id: number,
    sea_start_point_id: number | null,
    sea_end_point_id: number | null,
    rail_start_point_id: number | null,
    rail_end_point_id: number | null,
    start_date: number,
    end_date: number,
    price: number,
    currency: string,
}
export interface deleteDropRequest {
    ids: number[]
}


export interface editDropRequest {
    drop_id: number;
    company_id?: number;
    container_id?: number;
    sea_start_point_id?: number | null;
    sea_end_point_id?: number | null;
    rail_start_point_id?: number | null;
    rail_end_point_id?: number | null;
    start_date?: number;
    end_date?: number;
    price?: number;
    currency?: "USD";
}
