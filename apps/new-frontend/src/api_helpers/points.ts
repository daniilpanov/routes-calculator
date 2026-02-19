import type { IdType } from "@/interfaces/EntityWithId";
import type { IPoint } from "@/interfaces/Point";
import type { IDataOrError, IDataWithErrors } from "@/interfaces/APIResponses";

import { fetchAsJSON } from "@/helpers/requests.ts";

export async function getAllPoints(): Promise<IDataWithErrors<IPoint[]>> {
    return (await fetchAsJSON(`/api/points`)) as IDataWithErrors<IPoint[]>;
}

export async function getDepartures(date: string): Promise<IDataOrError<IdType[]>> {
    return (await fetchAsJSON(`/api/points/departures?date=${date}`)) as IDataOrError<IdType[]>;
}

export async function getDestinations(
    date: string,
    departureId: string | number
): Promise<IDataOrError<IdType[]>> {
    return (await fetchAsJSON(
        `/api/points/destinations?date=${date}&departure_point_id=${departureId}`
    )) as IDataOrError<IdType[]>;
}
