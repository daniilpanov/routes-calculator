import logo from "@/resources/images/logo.png";
import menuIcon from "@/resources/images/menu-icon.svg";
import closeIcon from "@/resources/images/close-icon.svg";
import "rsuite/Button/styles/index.css";
import "rsuite/Col/styles/index.css";
import "rsuite/Row/styles/index.css";
import "@/resources/scss/sidebar_style.scss";
import { ROUTES } from "@/constants";
import { logout, getUserName, isAuth } from "@/services/Auth";
import { useEffect, useState, FormEvent } from "react";
import { NavLink } from "react-router-dom";
import { Button, Col, Row } from "rsuite";


export function Sidebar() {
    const [ currentUser, setCurrentUser ] = useState(getUserName);
    const [ show, setShow ] = useState(false);

    useEffect(() => {
        if (isAuth())
            setCurrentUser(getUserName());
    }, []);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        await logout();
        setCurrentUser(null);
    };


    return (
        <div className={ show ? "sidebar show" : "sidebar" }>
            <div id="navToggler" onClick={ () => setShow(!show) }>
                <img src={ show ? closeIcon : menuIcon } width="30" alt="Toggle Sidebar" />
            </div>

            <div className="logo-wrapper"><img src={ logo } alt="Логотип" className="logo" /></div>

            <div className="mobile-space"></div>

            <div className="nav-block">
                <NavLink to={ ROUTES.DASHBOARD } className="nav-btn">Панель инструментов</NavLink>
                <NavLink to={ ROUTES.ROUTES_MANAGEMENT } className="nav-btn">Управление маршрутами</NavLink>
                <NavLink to={ ROUTES.POINTS_MANAGEMENT } className="nav-btn">Управление точками</NavLink>
                <NavLink to={ ROUTES.DATA_IMPORT } className="nav-btn">Загрузка данных</NavLink>
            </div>

            <div>
                <Row className="authentication-block">
                    <Col><div className="nav-btn">{ currentUser }</div></Col>
                    <Col><button onClick={ handleSubmit } className="nav-btn">Выйти</button></Col>
                </Row>

                <div className="back_to_site-block">
                    <NavLink to={ ROUTES.MAIN_SITE } className="nav-btn">Вернуться на сайт</NavLink>
                </div>
            </div>
        </div>
    );
}
