import { isAuth } from "@/services/Auth";
import { Navigate } from "react-router-dom";
import React from "react";
import Element = React.JSX.Element;


interface IRequireAuthProps {
    fallbackURL: string;
    children: Element;
}

export default function RequireAuth({ children, fallbackURL }: IRequireAuthProps) {
    return isAuth() ? <>{ children }</> : <Navigate to={ fallbackURL } replace />;
}
