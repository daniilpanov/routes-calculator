import type { IdIsExternal } from "@/interfaces/Point";

export const serializeId = ({ id, isExternal }: IdIsExternal): string =>
    `${isExternal ? "E" : "I"}${id}`;

export const serializeIds = (idIsExternalArray: IdIsExternal[]): string =>
    idIsExternalArray.map(serializeId).join(",");

export function deserializeId(serialized: string): IdIsExternal {
    const isExternal = serialized[0] === "E";
    serialized = serialized.slice(1);

    const id = Number.isNaN(Number(serialized)) ? serialized : Number(serialized);
    return { id, isExternal };
}

export const deserializeIds = (serialized: string): IdIsExternal[] =>
    serialized.split(",").map(deserializeId);
