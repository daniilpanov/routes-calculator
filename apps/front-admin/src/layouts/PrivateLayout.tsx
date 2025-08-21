// PublicLayout.tsx
import { Outlet } from "react-router-dom";
import "resources/scss/main_style.scss";

export default function PublicLayout() {
    return (
        <div className="app-container">
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    );
}
