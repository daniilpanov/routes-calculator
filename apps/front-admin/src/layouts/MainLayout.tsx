import { Outlet } from "react-router-dom";
import { Col, Row } from "rsuite";

import "rsuite/Row/styles/index.css";
import "rsuite/Col/styles/index.css";

import "@/resources/images/logo.png";
import "@/resources/scss/main_style.scss";

import Sidebar from "@/widgets/Sidebar";


export default function MainLayout() {
    return (
        <Row className="app-container">
            <Col className="sidebar-col"><Sidebar /></Col>
            <Col className="main-col">
                <main className="main-container">
                    <Outlet />
                </main>
            </Col>
        </Row>
    );
}
