import { Container } from "./Containers";
import { Point } from "./Points";
import { Company } from "./Companies";
import { PriceItem } from "./Prices";



export interface Route {
    id: number;
    company: Company;
    container: Container;
    start_point: Point;
    end_point: Point;
    effective_from: string;
    effective_to: string;
    price: PriceItem[];
    route_type: "rail" | "sea";
}

export interface GetRoutesResponse {
    status: string;
    count: number;
    routes: Route[];
}

export interface DeleteRouteResponse {
    status: string;
    route_id: number;
}


export interface CreateRouteResponse {
    status: string;
    new_route: Route;
}
export interface RouteCreateRequest {
    route_type: string
    company_id: number;
    container_id: number;
    start_point_id: number;
    end_point_id: number;
    effective_from: string;
    effective_to: string;
    price: {
        [key: string]: number;
    };
}

export interface RouteDeleteRequest {
    rail: number[];
    sea: number[];
}
export interface RouteEditResponse {
    status: string;
    edit_params: Route;
}

export interface RailPrice {
    price: number;
    drop: number;
    guard: number;
}

export interface SeaPrice {
    fifo: number;
    filo: number;
}

export interface RouteEditParams {
    start_point_id: number;
    end_point_id: number;
    company_id: number;
    container_id: number;
    effective_from: string;
    effective_to: string;
    route_type: "rail" | "sea";
    price: RailPrice | SeaPrice;
}


export interface RouteEditRequest {
    route_id: number;
    edit_params: RouteEditParams;
}
