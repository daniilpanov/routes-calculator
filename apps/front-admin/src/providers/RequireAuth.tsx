import React from "react";
import { Navigate } from "react-router-dom";
import Element = React.JSX.Element;

import { isAuth } from "@/services/Auth";


interface IRequireAuthProps {
    fallbackURL: string;
    children: Element;
}

export default function RequireAuth({ children, fallbackURL }: IRequireAuthProps) {
    return isAuth() ? <>{ children }</> : <Navigate to={ fallbackURL } replace />;
}
