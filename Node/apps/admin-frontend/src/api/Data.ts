import { API_ENDPOINTS } from "./ApiConfig";
import { UpdateResponse } from "@/interfaces/Data";
import axios from "axios";

export const updateFromGsheets = async (): Promise<UpdateResponse> =>
    (await axios.post(
        `${API_ENDPOINTS.DATA.UPDATE_FROM_GSHEETS}`,
        null,
        { withCredentials: true },
    )).data;

export const deleteAllData = async (): Promise<void> =>
    await axios.delete(
        `${API_ENDPOINTS.DATA.DB}`,
        { withCredentials: true },
    );

export async function uploadBackup(file: File): Promise<void> {
    const formData = new FormData();
    formData.append("dump_file", file);

    await axios.post(
        `${API_ENDPOINTS.DATA.DB}`,
        formData,
        {
            headers: { "Content-Type": "multipart/form-data" },
            withCredentials: true,
        },
    );
}
