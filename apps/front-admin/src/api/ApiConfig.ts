export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: "/admin/api/user/login",
        LOGOUT: "/admin/api/user/logout",
        REFRESH: "/admin/api/user/token/refresh",
        ME: "/admin/api/user/me",
    },
    ROUTES: {
        GET: "/admin/api/routes/",
        CREATE: "/admin/api/routes/add",
        DELETE: "/admin/api/routes/delete",
        EDIT: "/admin/api/routes/edit",
    },
    POINTS: {
        SEARCH: "/admin/api/points/{point_name}/",
        GET: "/admin/api/points",
        ADD: "/admin/api/points/add",
    },
    CONTAINERS: {
        GET: "/admin/api/container/",
    },
    COMPANIES: {
        GET: "/admin/api/company/",
    },
    DROPS: {
        GET: "/admin/api/drop/",
    },
};
