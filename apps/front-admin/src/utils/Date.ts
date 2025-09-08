export function formatDate(dateString: string) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const year = date.getFullYear();

    return `${day}.${month}.${year}`;
}
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
};
export function parseWeirdDate(dateString: string): string {
    if (!dateString) return "";

    const match = dateString.match(/(\d{2})T\d{2}:\d{2}:\d{2}\.(\d{2})\.(\d{4})/);
    if (!match) return "";

    const day = match[1].padStart(2, "0");
    const month = match[2].padStart(2, "0");
    const year = match[3];

    return `${day}.${month}.${year}`;
}


