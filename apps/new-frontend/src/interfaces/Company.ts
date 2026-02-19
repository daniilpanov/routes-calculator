import type { IEntityWithId } from "@/interfaces/EntityWithId";

export interface ICompany extends IEntityWithId {
    id: number;
    name: string;
}
