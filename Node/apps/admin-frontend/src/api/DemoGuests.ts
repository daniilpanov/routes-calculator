import { API_ENDPOINTS } from "./ApiConfig";
import type { IDemoGuest, IDemoGuestPayload } from "@/interfaces/DemoGuest";
import axios from "axios";

export const listDemoGuests = async (): Promise<IDemoGuest[]> =>
    (await axios.get(API_ENDPOINTS.DEMO_GUESTS.ROOT, { withCredentials: true })).data;

export const createDemoGuest = async (payload: IDemoGuestPayload): Promise<IDemoGuest> =>
    (await axios.post(API_ENDPOINTS.DEMO_GUESTS.ROOT, payload, { withCredentials: true })).data;

export const updateDemoGuest = async (id: number, payload: IDemoGuestPayload): Promise<IDemoGuest> =>
    (await axios.put(API_ENDPOINTS.DEMO_GUESTS.byId(id), payload, { withCredentials: true })).data;

export const deleteDemoGuest = async (id: number): Promise<void> =>
    await axios.delete(API_ENDPOINTS.DEMO_GUESTS.byId(id), { withCredentials: true });
