export const BASE_API_URL = "";

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: "api/user/login",
        LOGOUT: "api/user/logout",
        REFRESH: "api/user/refresh",
    },
} as const;
