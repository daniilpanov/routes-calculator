import { createBrowserRouter, Navigate } from "react-router-dom";
import { ROUTES } from "./RoutesConst";
import Login from "../pages/Login";
import Dashboard from "../pages/Dashboard";
import RoutesManagement from "../pages/RoutesManagement";
import PointsManagement from "../pages/PointsManagement";
import DataImport from "../pages/DataImport";
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
                    { path: ROUTES.ROUTES_MANAGEMENT, element: <RoutesManagement /> },
                    { path: ROUTES.POINTS_MANAGEMENT, element: <PointsManagement /> },
                    { path: ROUTES.DATA_IMPORT, element: <DataImport /> },
                    { path: ROUTES.ROOT, element: <Navigate to={ ROUTES.DASHBOARD } replace /> },
                ],
            },
        ],
    },
];


export const router = createBrowserRouter(routesConfig);
