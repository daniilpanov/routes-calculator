export interface IDataWithErrors<DT> {
    errors: Record<string, { error_text: string, error_type: string }>;
    data: DT;
}
