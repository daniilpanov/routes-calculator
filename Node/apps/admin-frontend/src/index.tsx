import React from "react";
import ReactDOM from "react-dom/client";
import { onStartup } from "@/services/Auth";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root")!);

onStartup();

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
