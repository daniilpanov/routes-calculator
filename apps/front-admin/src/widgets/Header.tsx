import { NavLink } from "react-router-dom";
import { ROUTES } from "../services/RoutesConst";
import "../resources/scss/header_style.scss";
import logo from "../resources/images/logo1.png";
import React, { useEffect, useState } from "react";
import { authService } from "../services/Auth";
import { useNavigate } from "react-router-dom";


export function Header() {
    const [ currentUser, setCurrentUser ] = useState(() => {
        return localStorage.getItem("username") || null;
    });
    const [ loading, setLoading ] = useState(false);
    const navigate = useNavigate();


    useEffect(() => {
        const username = localStorage.getItem("username");
        if (username) {
            setCurrentUser(username);
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await authService.logout();
            if (response.status === "OK") {
                setCurrentUser(null);
                localStorage.removeItem("username");
            }

            navigate(ROUTES.LOGIN);
        } catch (err) {
            console.error("Login error:", err);
        } finally {
            setLoading(false);
        }
    };


    return (
        <header className="app_header">
            <div className="logo_div"><img src={ logo } alt="Логотип" className="logo_img" /></div>
            <div className="nav_div">
                <NavLink to={ ROUTES.DASHBOARD } className="nav_btn">Панель инструментов</NavLink>
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="nav_btn">Управление маршрутами</NavLink>
                <NavLink to={ ROUTES.POINTS_MANAGEMENT } className="nav_btn">Управление точками</NavLink>
                <NavLink to={ ROUTES.DATA_IMPORT } className="nav_btn">Загрузка данных</NavLink>
            </div>
            <div className="authentication_div">
                <p className="nav_btn">{currentUser}</p>
                <p onClick={ handleSubmit } className="nav_btn">Выйти</p>
            </div>

            <div className="back_to_off_site_div">
                <NavLink to={ ROUTES.MAIN_SITE } className="nav_btn">Вернуться на сайт</NavLink>
            </div>
        </header>

    );
}
