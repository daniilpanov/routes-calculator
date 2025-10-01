import { Outlet } from "react-router-dom";

import "@/resources/images/logo.png";
import "@/resources/scss/main_style.scss";

export default function MainLayout() {
    return (
        <div className="app-container">
            <main className="main-container">
                <Outlet />
            </main>
        </div>
    );
}
