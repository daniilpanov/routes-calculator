export interface Container {
    weight_from: number,
    name: string,
    id: number,
    size: number,
    weight_to: number,
    type: string,
}
export interface ContainersResponse {
    status: "OK",
    containers: Container[],
}
