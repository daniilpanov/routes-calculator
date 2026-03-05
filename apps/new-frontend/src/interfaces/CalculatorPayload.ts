import type { IdIsExternal } from "@/interfaces/Point";

export interface ICalculatorReadyToSendPayload {
    dispatchDate?: string;
    showAllRoutes?: boolean;
    departureInternalIds: number[];
    destinationInternalIds: number[];
    departureExternalIds: string[];
    destinationExternalIds: string[];
    containerType?: string;
    cargoWeight?: number;
    currency: string;
}

export interface ICalculatorPayload {
    date?: string;
    showAllRoutes?: boolean;
    departureIds?: IdIsExternal[];
    destinationIds?: IdIsExternal[];
    containerType?: string;
    containerWeight?: number;
}

export interface ICalculatorPayloadWithCurrency extends ICalculatorPayload {
    currency?: string;
}
