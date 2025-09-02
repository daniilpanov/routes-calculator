import { createBrowserRouter } from "react-router-dom";
import { ROUTES } from "./constants";
import MainLayout from "@/layouts/MainLayout";
import Dashboard from "@/pages/Dashboard";
import React from "react";

export const routesConfig = [
    {
        element: <MainLayout />,
        children: [
            { path: ROUTES.ROOT, element: <Dashboard /> },
            { path: ROUTES.DASHBOARD, element: <Dashboard /> },
        ],
    },
];

export default createBrowserRouter(routesConfig);
