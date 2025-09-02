import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
    plugins: [ react() ],
    base: process.env.VITE_PUBLIC_URL,
    resolve: {
        alias: {
            "@": resolve(__dirname, "src"),
        },
    },
    server: {
        port: process.env.PORT || 3000,
        allowedHosts: true,
    },
});
