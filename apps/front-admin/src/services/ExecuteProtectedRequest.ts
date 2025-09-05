import { refresh } from "@/api/Auth";
import { AxiosError, AxiosResponse } from "axios";

export default async function ExecuteProtectedRequest<T = any>(requestCoro: (...args: any[]) => Promise<AxiosResponse<T>>, ...args: any[]): Promise<AxiosResponse<T>> {
    try {
        return await requestCoro(...args);
    } catch (e) {
        const error = e as AxiosError;
        if (error.response?.status !== 401 && error.response?.status !== 422)
            throw e;

        await refresh();
        return await requestCoro(...args);
    }
}
