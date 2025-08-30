import "@/resources/images/logo.png";
import { Outlet } from "react-router-dom";

export default function MainLayout() {
    return (
        <div className="app-container">
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}
