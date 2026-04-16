export const ROUTES = {
    ROOT: import.meta.env.VITE_PUBLIC_URL || "/",
    LOGIN: `${import.meta.env.VITE_PUBLIC_URL || ""}/login`,
    DASHBOARD: `${import.meta.env.VITE_PUBLIC_URL || ""}/dashboard`,
    ROUTES_MANAGEMENT: `${import.meta.env.VITE_PUBLIC_URL || ""}/routes-management`,
    POINTS_MANAGEMENT: `${import.meta.env.VITE_PUBLIC_URL || ""}/points-management`,
    DATA_IMPORT: `${import.meta.env.VITE_PUBLIC_URL || ""}/data-import`,
    MAIN_SITE: import.meta.env.VITE_REACT_ROUTING_MAIN_SITE || "/",
};

export const LOGIN_CHECK_INTERVAL = 60 * 1000;
