import "@/resources/images/logo.png";
import "@/resources/scss/main_style.scss";
import { Outlet } from "react-router-dom";

export default function MainLayout() {
    return (
        <div className="app-container">
            <main className="main-container">
                <Outlet />
            </main>
        </div>
    );
}
