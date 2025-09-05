import { createBrowserRouter } from "react-router-dom";
import { ROUTES } from "./constants";
import MainLayout from "@/layouts/MainLayout";
import Dashboard from "@/pages/Dashboard";
import RequireAuth from "@/providers/RequireAuth";
import React from "react";
import Element = React.JSX.Element;
import EmptyLayout from "@/layouts/EmptyLayout";
import Login from "@/pages/Login";

function createSecureRoute(layout: Element) {
    return RequireAuth({
        children: layout,
        fallbackURL: ROUTES.LOGIN,
    });
}

export const routesConfig = [
    {
        element: <EmptyLayout />,
        children: [
            { path: ROUTES.LOGIN, element: <Login /> },
        ],
    },
    {
        element: createSecureRoute(<MainLayout />),
        children: [
            { path: ROUTES.ROOT, element: <Dashboard /> },
            { path: ROUTES.DASHBOARD, element: <Dashboard /> },
        ],
    },
];

export default createBrowserRouter(routesConfig);
