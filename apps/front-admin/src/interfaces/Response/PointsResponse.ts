import { Point } from "../Points";

export interface PointsGetResponse {
    status: string;
    count: number;
    points: Point[]
}
export interface searchPointsResponse {
    status: string;
    point_name: Point[];
}
