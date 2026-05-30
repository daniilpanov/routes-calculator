export interface IDemoGuest {
    id: number;
    uid: string;
    sea_profit: number;
    sea_profit_currency: string;
    rail_profit: number;
    rail_profit_currency: string;
}

export interface IDemoGuestPayload {
    uid: string;
    sea_profit: number;
    sea_profit_currency: string;
    rail_profit: number;
    rail_profit_currency: string;
}
