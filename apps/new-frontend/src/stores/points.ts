import { ref } from "vue";
import { defineStore } from "pinia";
import type { IPoint } from "@/interfaces/Point";

export const usePoints = defineStore("points", () => {
    const points = ref<IPoint[]>([]);
    const pointsIndexedById = ref<Map<string | number, IPoint>>(new Map());

    const setPoints = (newPoints: IPoint[]) => {
        points.value = newPoints;

        pointsIndexedById.value.clear();
        for (const point of newPoints) pointsIndexedById.value.set(point.id, point);
    };

    return { points, setPoints, pointsIndexedById };
});
