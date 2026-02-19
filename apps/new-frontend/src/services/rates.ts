import { getRates } from "@/api_helpers/rates";
import { useRates } from "@/stores/rates";

export async function updateRates() {
    const { setRates, setCurrentRate } = useRates();

    setRates(await getRates());
    if (!useRates().currentRate) setCurrentRate("RUB");
}

export const lockRates = async (coro: Promise<void>) => useRates().setLocker(coro);
