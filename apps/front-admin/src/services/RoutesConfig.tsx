import { createBrowserRouter, Navigate } from "react-router-dom";
import { ROUTES } from "./RoutesConst";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import Routes_management from "../pages/Routes_management";
import Points_management from "../pages/Points_management";
import Data_import from "../pages/Data_import";
import PrivateRoute from "../layouts/PrivateRoute";
import PublicLayout from "../layouts/PrivateLayout";
import PrivateLayout from "../layouts/PublicLayout";



export const routesConfig = [
    {
        element: <PublicLayout />,
        children: [
            { path: ROUTES.LOGIN, element: <Login /> },
            { path: ROUTES.MAIN_SITE, element: <Navigate to={ ROUTES.MAIN_SITE } replace /> },
        ],
    },
    {
        element: <PrivateRoute />,
        children: [
            {
                element: <PrivateLayout />,
                children: [
                    { path: ROUTES.DASHBOARD, element: <Dashboard /> },
                    { path: ROUTES.ROUTES_MANAGEMENT, element: <Routes_management /> },
                    { path: ROUTES.POINTS_MANAGEMENT, element: <Points_management /> },
                    { path: ROUTES.DATA_IMPORT, element: <Data_import /> },
                    { path: ROUTES.ROOT, element: <Navigate to={ ROUTES.DASHBOARD } replace /> },
                ],
            },
        ],
    },
];


export const router = createBrowserRouter(routesConfig);
