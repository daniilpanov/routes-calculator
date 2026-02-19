import type { MapObject } from "@/interfaces/MapObject";
import { fetchAsJSON } from "@/helpers/requests.ts";

export async function getRates(): Promise<MapObject<number>> {
    return (await fetchAsJSON("/api/rates/")) as MapObject<number>;
}
