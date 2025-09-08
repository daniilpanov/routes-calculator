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
        EDIT: "api/routes/edit",
    },
    POINTS: {
        SEARCH: "api/points/find_name",
        GET: "api/points",
        ADD: "api/points/add",
    },
    CONTAINERS: {
        GET: "api/container",
    },
    COMPANIES: {
        GET: "api/company",
    },
} as const;
