import { getAllPoints } from "@/api_helpers/points";
import { usePoints } from "@/stores/points";

export async function updateAllPoints() {
    const { setPoints } = usePoints();

    setPoints((await getAllPoints()).data);
}
