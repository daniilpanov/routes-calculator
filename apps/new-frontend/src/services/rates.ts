import { getRates } from "@/api_helpers/rates";
import { useRates } from "@/stores/rates";

export async function updateRates() {
    const { setRates, setCurrentRate } = useRates();

    setRates(await getRates());
    if (!useRates().currentRate) setCurrentRate("RUB");
}

export const lockRates = async (coro: Promise<void>) => useRates().setLocker(coro);

export const isConversationNeeded = (currency: string) =>
    ["RUB", "RUR", "РУБ"].indexOf(currency) === -1;

export function convertToCurrentRate(value: number, fromCurrency: string, percents?: number): [number, number] {
    const { rates, currentRateValue } = useRates();
    if (!currentRateValue) throw new Error("No current rate selected!");

    const fromRate = rates.get(fromCurrency);
    if (!fromRate) throw new Error(`Invalid currency: ${fromCurrency}`);

    const result = value / currentRateValue * fromRate;

    percents = isConversationNeeded(fromCurrency) ? percents ?? 0 : 0;
    const resultWithConv = result * (1 + percents / 100);

    return [result, resultWithConv];
}
