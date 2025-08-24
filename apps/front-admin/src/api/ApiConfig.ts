export const BASE_API_URL = "";

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: "api/user/login",
        LOGOUT: "api/user/logout",
        REFRESH: "api/user/refresh",
    },
    ROUTES: {
        GET: "api/user/routes",
        CREATE: "api/user/routes/add",
        DELETE: "api/user/routes/delete",
    },
    POINTS: {
        SEARCH: "api/user/point/find_name",
    },
} as const;
