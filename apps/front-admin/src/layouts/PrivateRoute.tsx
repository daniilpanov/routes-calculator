import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";

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

    return currentUser ? <Outlet /> : <Navigate to="/admin/login" replace />;
}
