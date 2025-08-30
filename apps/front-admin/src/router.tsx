import { createBrowserRouter } from "react-router-dom";
import { ROUTES } from "./constants";
import MainLayout from "@/layouts/MainLayout";
import Dashboard from "@/pages/Dashboard";

export const routesConfig = [
    {
        element: <MainLayout />,
        children: [
            { path: ROUTES.ROOT, element: <Dashboard /> },
        ],
    },
];

export const router = createBrowserRouter(routesConfig);
