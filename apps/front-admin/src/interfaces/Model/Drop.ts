import { Company } from "@/interfaces/Companies";
import { Container } from "@/interfaces/Containers";
import { Point } from "@/interfaces/Points";

export interface Drop {
    id: number;
    company: Company;
    container: Container;
    sea_start_point: Point | null;
    sea_end_point: Point | null;
    rail_start_point: Point | null;
    rail_end_point: Point | null;
    start_date: number;
    end_date: number;
    price: number;
    currency: string;
}
