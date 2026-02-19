import { fetchAsJSON } from "@/helpers/requests.ts";

export async function getRoutes(
    dispatchDate: string,
    showAllRoutes: boolean,
    departureId: string | number,
    destinationId: string | number,
    cargoWeight: number,
    containerType: number
) {
    return await fetchAsJSON("/api/routes/calculate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            dispatchDate,
            showAllRoutes,
            departureId,
            destinationId,
            cargoWeight,
            containerType,
        }),
    });
}
