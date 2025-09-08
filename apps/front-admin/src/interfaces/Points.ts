export interface PointsSearchResponse {
    status: string;
    point_name: Point[];
}

export interface Point {
    id: number;
    RU_city: string;
    RU_country: string;
    country: string;
    city: string;
}
export interface PointsGetResponse{
    status: string;
    points: Point[];
}
export interface PointsAddRequest {
    "city": string,
    "country": string,
    "RU_city": string,
    "RU_country": string,
}
export interface PointAddResponse {
    status: string;
    new_point: Point;
}
