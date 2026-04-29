import { useRouter } from "@/stores/router";

export const gotoAuthForm = () =>
    useRouter().router!.push({ path: "/login" });

export const gotoHome = () =>
    useRouter().router!.push({ path: "/" });
