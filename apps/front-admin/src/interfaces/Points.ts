export interface PointsSearchResponse {
    status: string;
    point_name: Point[];
}

export interface Point {
    id: number;
    RU_city: string;
    RU_country: string;
}
