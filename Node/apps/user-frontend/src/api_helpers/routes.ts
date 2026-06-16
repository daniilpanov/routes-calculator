import type { IError } from "@/interfaces/APIResponses";
import type { ICalculatorReadyToSendPayload } from "@/interfaces/CalculatorPayload";
import type { RouteDescriptor, Route, IDrop } from "@/interfaces/Routes";
import type { IService } from "@/interfaces/Service";
import { fetchSSE } from "@/helpers/requests";

interface RouteResultSSE {
    segments: Route;
    drop: IDrop;
    may_be_invalid: boolean;
    services: IService[];
}

export async function* getRoutesSSE(
    payload: ICalculatorReadyToSendPayload,
): AsyncGenerator<{ type: "route"; route: RouteDescriptor } | { type: "error"; error: IError }> {
    const stream = fetchSSE("/api/v3/routes/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    }, 40000);

    for await (const { event, data } of stream) {
        if (event === "route") {
            const result: RouteResultSSE = JSON.parse(data);
            const route: RouteDescriptor = [
                result.segments,
                result.drop,
                result.may_be_invalid,
                result.services,
            ];
            yield { type: "route", route };
        } else if (event === "error") {
            const error: IError = JSON.parse(data);
            yield { type: "error", error };
        } else if (event === "complete") {
            break;
        }
    }
}
