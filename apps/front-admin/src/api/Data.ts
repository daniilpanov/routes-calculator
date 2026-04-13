import { API_ENDPOINTS } from "./ApiConfig";
import ExecuteProtectedRequest from "@/services/ExecuteProtectedRequest";
import axios from "axios";
import { UpdateResponse } from "@/interfaces/Data";

export async function updateFromGsheets(): Promise<UpdateResponse> {
    const response = await ExecuteProtectedRequest<UpdateResponse>(
        async () => axios.post(
            `${API_ENDPOINTS.DATA.UPDATE_FROM_GSHEETS}`,
            null,
            {
                withCredentials: true,
            },
        ),
    );
    return response.data;
}

export async function deleteAllData(): Promise<void> {
    await ExecuteProtectedRequest<void>(
        async () => axios.delete(
            `${API_ENDPOINTS.DATA.DB}`,
            {
                withCredentials: true,
            },
        ),
    );
}

export async function uploadBackup(file: File): Promise<void> {
    const formData = new FormData();
    formData.append("file", file);

    await ExecuteProtectedRequest<void>(
        async () => axios.post(
            `${API_ENDPOINTS.DATA.DB}`,
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                withCredentials: true,
            },
        ),
    );
}
