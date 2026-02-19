import { reactive } from "vue";
import { defineStore } from "pinia";
import type { IPoint } from "@/interfaces/Point";

type PointsData = {
    departures: IPoint[],
    destinations: IPoint[],
};

export const usePoints = defineStore("points", () => {
    const points = reactive<PointsData>({
        departures: [],
        destinations: [],
    });

    const setDepartures = (newPoints: IPoint[]) => points.departures = newPoints;

    const setDestinations = (newPoints: IPoint[]) => points.destinations = newPoints;

    return { setDepartures, setDestinations };
});
