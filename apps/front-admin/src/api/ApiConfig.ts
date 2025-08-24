export const BASE_API_URL = "";

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: "api/user/login",
        LOGOUT: "api/user/logout",
        REFRESH: "api/user/refresh",
    },
    ROUTES: {
        GET: "api/routes",
        CREATE: "api/routes/add",
        DELETE: "api/routes/delete",
    },
    POINTS: {
        SEARCH: "api/points/find_name",
    },
} as const;
