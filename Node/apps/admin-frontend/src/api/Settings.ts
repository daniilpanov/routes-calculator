import { API_ENDPOINTS } from "./ApiConfig";
import type { ISetting, ISettingPayload } from "@/interfaces/Setting";
import axios from "axios";

const ROOT = API_ENDPOINTS.SETTINGS.ROOT;

export const listSettings = async (group?: string, q?: string): Promise<ISetting[]> => {
    const params: Record<string, string> = {};
    if (group) params.group = group;
    if (q) params.q = q;
    return (await axios.get(ROOT, { params, withCredentials: true })).data;
};

export const createSetting = async (payload: ISettingPayload): Promise<ISetting> =>
    (await axios.post(ROOT, payload, { withCredentials: true })).data;

export const updateSetting = async (id: number, payload: ISettingPayload): Promise<ISetting> =>
    (await axios.put(API_ENDPOINTS.SETTINGS.byId(id), payload, { withCredentials: true })).data;

export const deleteSetting = async (id: number): Promise<void> =>
    await axios.delete(API_ENDPOINTS.SETTINGS.byId(id), { withCredentials: true });
