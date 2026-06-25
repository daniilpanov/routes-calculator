export interface ISetting {
    id: number;
    group: string;
    name: string;
    description: string | null;
    value_type: string;
    value: string | null;
}

export interface ISettingPayload {
    group: string;
    name: string;
    description: string | null;
    value_type: string;
    value: string | null;
}
