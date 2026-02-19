export interface IDataResponse<DT> {
    status: true;
    data: DT;
}

export interface IErrorResponse {
    status: false;
    error: string;
    type: string;
}

export type IDataOrError<DT> = IDataResponse<DT> | IErrorResponse;

export interface IDataWithErrors<DT> {
    errors: { [key: string]: { error_text: string, error_type: string } };
    data: DT;
}
