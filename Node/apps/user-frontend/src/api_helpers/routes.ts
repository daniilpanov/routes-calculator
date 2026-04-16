import type { ICalculatorResult } from "@/interfaces/APIResponses";
import type { ICalculatorReadyToSendPayload } from "@/interfaces/CalculatorPayload";
import { fetchAsJSON } from "@/helpers/requests";

export const getRoutes = async (payload: ICalculatorReadyToSendPayload): Promise<ICalculatorResult> =>
    await fetchAsJSON("/api/v2/routes/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    }) as ICalculatorResult;
