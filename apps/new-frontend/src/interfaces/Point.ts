import type { ICompany } from "./Company";
import type { IEntityWithId } from "./EntityWithId";

export interface IPoint extends IEntityWithId {
    translates: Map<string, ITranslatePoint>;
    ports: IPort[];
    companies: ICompany[];
}

export interface IPort extends IEntityWithId {
    translates: Map<string, ITranslatePort>;
    companies: ICompany[];
}

export interface ITranslate {
    entityId: string | number;
    lang: string;
}

export interface ITranslatePoint extends ITranslate {
    name: string;
    country: string;
}

export interface ITranslatePort extends ITranslate {
    name: string;
}
