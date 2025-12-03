import { Container } from "@/interfaces/Containers";

export interface getContainersResponse {
    status: string
    containers: Container[],
}
