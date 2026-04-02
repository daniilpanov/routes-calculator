// boolean = selected in commercial proposal
export type RouteExtendedDescriptor = [...RouteDescriptor, PriceDescriptor, PriceDescriptor, boolean];
export type PriceDescriptor = number | PriceRange;
export type PriceRange = [number, number];
export type RouteDescriptor = [Route, IDrop, boolean];  // boolean = isEffective
export type Route = (ISinglePriceSegment | IMultiPriceSegment)[];

export enum RouteType {
    SEA = "SEA",
    RAIL = "RAIL",
    SEA_RAIL = "SEA_RAIL",
}

export interface ICalculatorExtendedResult {
    oneService: RouteExtendedDescriptor[];
    multiService: RouteExtendedDescriptor[];
}

export interface IDrop {
    price: number;
    currency: string;
    conversation_percents: number;
}

interface ISegment {
    company: string;
    type: RouteType;

    effectiveFrom: string;
    effectiveTo: string;

    startPointName: string;
    startPointCountry: string;
    endPointName: string;
    endPointCountry: string;

    comment?: string;
}

export interface IMultiPriceSegment extends ISegment {
    prices: IPrice[];
}

export interface ISinglePriceSegment extends ISegment {
    beginCond?: string;
    finishCond?: string;
    container: IContainer;
    price: number;
    currency: string;
}

export interface IPrice {
    transfer_terms: string;
    shipment_terms: string;
    conversation_percents: number;
    currency: string;
    value: number;
    container: IContainer;
}

export interface IContainer {
    name: string;
    size: number;
    type: "HC" | "DC";
    weight_from: number;
    weight_to: number;
}
