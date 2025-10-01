import React from "react";
import { createBrowserRouter } from "react-router-dom";

import { ROUTES } from "./constants";
import MainLayout from "@/layouts/MainLayout";
import EmptyLayout from "@/layouts/EmptyLayout";
import RequireAuth from "@/providers/RequireAuth";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";


export const routesConfig = [
    {
        element: <EmptyLayout />,
        children: [
            { path: ROUTES.LOGIN, element: <Login /> },
        ],
    },
    {
        element: <RequireAuth fallbackURL={ ROUTES.LOGIN }><MainLayout /></RequireAuth>,
        children: [
            { path: ROUTES.ROOT, element: <Dashboard /> },
            { path: ROUTES.DASHBOARD, element: <Dashboard /> },
        ],
    },
];

export default createBrowserRouter(routesConfig);
