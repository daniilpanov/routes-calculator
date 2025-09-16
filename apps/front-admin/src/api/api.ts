import axios from "axios";

export const api = axios.create({
    baseURL: "/admin",
    withCredentials: true,
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
    },
    validateStatus: (status) => status >= 200 && status < 300,
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (axios.isAxiosError(error)) {
            if (error.response) {
                console.error(
                    "API Error:",
                    error.response.status,
                    error.response.data,
                );
                return Promise.reject(
                    new Error(
                        `Ошибка API (${error.response.status}): ${
                            error.response.data?.detail || JSON.stringify(error.response.data)
                        }`,
                    ),
                );
            } else if (error.request) {
                return Promise.reject(new Error("Сервер не отвечает"));
            } else {
                return Promise.reject(new Error(error.message));
            }
        }
        return Promise.reject(new Error("Неизвестная ошибка"));
    },
);
