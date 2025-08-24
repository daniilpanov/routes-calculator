export interface Container {
    id: number;
    name: string;
    weight_from: number;
    weight_to: number;
    size: number;
    type: string;
}

export interface Point {
    id: number;
    RU_city: string;
    RU_country: string;
    city: string;
    country: string;
}

export interface Company {
    id: number;
    name: string;
}
export interface PriceItem {
    type: string;
    value: number | null;
    currency: string;
}

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

/*
export interface CreateRouteResponse {
    status: string;
    new_route:
}
*/
export interface DeleteRouteResponse {
    status: string;
    route_id: number;
}
