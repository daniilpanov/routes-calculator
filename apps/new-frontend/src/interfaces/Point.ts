import type { IdType } from "@/interfaces/EntityWithId";
import type { ICompany } from "./Company";

export type IdIsExternal = { id: IdType, isExternal: boolean };

export interface IPointIds {
    ids: number[];
    external_ids: string[];
}

export interface IPoint extends IPointIds {
    translates: Record<string, ITranslatePoint>;
    ports: IPort[];
    companies: ICompany[];
}

export interface IPort extends IPointIds {
    translates: Record<string, ITranslatePort>;
    companies: ICompany[];
}

export interface ITranslatePoint {
    name: string;
    country: string;
}

export interface ITranslatePort {
    name: string;
}
