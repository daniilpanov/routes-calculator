export const formatDate = (date: string | number) =>
    new Date(date).toLocaleDateString();

export function formatDateISO(dateString: string) {
    if (!dateString) return "";

    if (dateString.includes(".")) {
        const [ day, month, year ] = dateString.split(".");
        return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
    }

    if (dateString.includes("-")) {
        return dateString;
    }

    return "";
}
export function formatDateForServerFromInput (date: string) {
    const [ year, month, day ] = date.split("-");
    if (!year || !month || !day) return "";
    return `${day}.${month}.${year}`;
}

export function parseDateFromTimestampToOutput(dateTimestamp: number) {
    if (!dateTimestamp) return "";

    const date = new Date(dateTimestamp*1000);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${day}.${month}.${year}`;
}
export function parseDateFromTimestampToInput(dateTimestamp: number) {
    if (!dateTimestamp) return "";

    const date = new Date(dateTimestamp*1000);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${year}-${month}-${day}`;
}

export function parseInputToTimestamp(dateString: string) {
    return Math.floor(new Date(dateString).getTime() / 1000);
}

