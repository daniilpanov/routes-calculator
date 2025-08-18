import { Point } from "../Points";

export interface PointsGetResponse {
    status: string;
    count: number;
    points: Point[]
}
