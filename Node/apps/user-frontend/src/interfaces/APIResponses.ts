import type { RouteDescriptor } from "./Routes";

export interface ICalculatorResult {
    errors: IError[];
    routes: RouteDescriptor[];
}

export interface ILoginResponse {
    status: string;
    accessTokenExpiredInMinutes?: number;
    refreshTokenExpiredInMinutes?: number;
}

export interface IError {
    source?: string;
    error_text: string;
    error_type: string;
}

export interface IDataWithErrors<DT> {
    errors: IError[];
    data: DT;
}
