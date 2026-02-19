import { fetchAsJSON } from "@/helpers/requests";

export const getRates = async (): Promise<Record<string, number>> =>
    (await fetchAsJSON("/api/v1/rates/")) as Record<string, number>;
