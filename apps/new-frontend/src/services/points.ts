import type { IdIsExternal } from "@/interfaces/Point";

export const serializeId = ({ id, isExternal }: IdIsExternal): string =>
    `${isExternal ? "E" : "I"}${id}`;

export const serializeIds = (idIsExternalArray: IdIsExternal[]): string =>
    idIsExternalArray.map(serializeId).join(",");
