export const dateToTimestamp = (date: Date): number => {
    return date.getTime();
};

export const timestampToDateString = (timestamp: number): string => {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
};
export const timestampToDateStringRU = (timestamp: string | number): string => {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${day}.${month}.${year}`;
};

export const dateStringToTimestamp = (dateString: string): number => {
    return new Date(dateString).getTime();
};
