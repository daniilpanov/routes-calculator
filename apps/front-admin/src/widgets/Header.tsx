import { NavLink } from "react-router-dom";
import { ROUTES } from "../layouts/RoutesConst";
import "../resources/scss/header_style.scss";
import logo from "../resources/images/logo1.png";
import { useState } from "react";


export function Header() {
    const [ user, setUser ] = useState(null);

    return (
        <header className="app_header">
            <div className="logo_div"><img src={ logo } alt="Логотип" className="logo_img" /></div>
            <div className="nav_div">
                <NavLink to={ ROUTES.DASHBOARD } className="nav_btn">Dashboard</NavLink>
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="nav_btn">Routs management</NavLink>
                <NavLink to={ ROUTES.POINTS_MANAGEMENT } className="nav_btn">Points management</NavLink>
                <NavLink to={ ROUTES.DATA_IMPORT } className="nav_btn">Data import</NavLink>
            </div>
            <div className="authentication_div">
                <NavLink to={ ROUTES.LOGIN } className="nav_btn">Павел</NavLink>
            </div>
            <div className="authentication_div">
                <NavLink to={ ROUTES.LOGIN } className="nav_btn">Войти</NavLink>
            </div>
            <div className="back_to_off_site_div">
                <NavLink to={ ROUTES.MAIN_SITE } className="nav_btn">Вернуться на сайт</NavLink>
            </div>

        </header>

    );
}
