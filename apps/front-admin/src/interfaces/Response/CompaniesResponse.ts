import { Company } from "@/interfaces/Companies";

export interface getCompaniesResponse {
    status: string,
    count: number
    companies: Company[],
}
