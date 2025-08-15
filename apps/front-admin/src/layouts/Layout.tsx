import { Outlet } from "react-router-dom";
import { Header } from "../widgets/Header";
import "resources/scss/main_style.scss";

export default function Layout() {
    return (
        <div className="app-container">
            <Header />
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}
