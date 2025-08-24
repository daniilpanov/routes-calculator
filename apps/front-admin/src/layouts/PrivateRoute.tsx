import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { ROUTES } from "../services/RoutesConst";

export default function PrivateRoute() {
    const [ currentUser, setCurrentUser ] = useState(() => {
        return localStorage.getItem("username") || null;
    });
    useEffect(() => {
        const username = localStorage.getItem("username");
        if (username) {
            setCurrentUser(username);
        }
    }, []);

    return currentUser ? <Outlet /> : <Navigate to={ ROUTES.LOGIN } replace />;
}
