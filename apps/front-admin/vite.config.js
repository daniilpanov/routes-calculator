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
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: "@import \"@/styles/variables.scss\";",
            },
        },
    },
    server: {
        port: process.env.PORT || 3000,
    },
});
