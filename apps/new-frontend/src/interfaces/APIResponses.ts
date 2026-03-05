import type { RouteDescriptor } from "./Routes";

export interface ICalculatorResult {
    errors: IError[];
    multi_service_routes: RouteDescriptor[];
    one_service_routes: RouteDescriptor[];
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
