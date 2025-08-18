import { createBrowserRouter, Navigate } from "react-router-dom";
import Layout from "./Layout";
import { ROUTES } from "./RoutesConst";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Routes_management from "../pages/Routes_management";
import Points_management from "../pages/Points_management";
import Data_import from "../pages/Data_import";

export const routesConfig = [
    {
        element: <Layout />,
        children: [
            { path: ROUTES.LOGIN, element: <Login /> },
            { path: ROUTES.DASHBOARD, element: <Dashboard /> },
            { path: ROUTES.ROUTES_MANAGEMENT, element: <Routes_management /> },
            { path: ROUTES.POINTS_MANAGEMENT, element: <Points_management /> },
            { path: ROUTES.DATA_IMPORT, element: <Data_import /> },
            { path: ROUTES.MAIN_SITE },
            { path: ROUTES.ROOT, element: <Dashboard /> },
        ],
    },
];

export const router = createBrowserRouter(routesConfig);
