import { api } from "./api"; // твой axios instance

export interface UploadSampleParams {
    route_type: string;
    type_data?: string | null;
    company_col?: string | null;
    company_name?: string | null;
    dates_col?: string | null;
    dates?: string | null;
    file: File;
}

export async function uploadSample(params: UploadSampleParams): Promise<any> {
    const {
        route_type,
        type_data,
        company_col,
        company_name,
        dates_col,
        dates,
        file,
    } = params;

    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/data/import", formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
        params: {
            route_type,
            type_data,
            company_col,
            company_name,
            dates_col,
            dates,
        },
    });

    return response.data;
}
