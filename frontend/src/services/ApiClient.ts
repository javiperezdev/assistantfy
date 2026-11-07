import axios from 'axios';
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

export const apiClient: AxiosInstance = axios.create({
    baseURL: "/API", // backend url (change to .env in production)
    timeout: 5000,                    // Aborts the request if the server takes longer than 5 seconds (prevents freezing)
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    // Send and receive cookies (session cookie) on every request.
    withCredentials: true,
});

apiClient.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            const requestUrl = (error.config as InternalAxiosRequestConfig | undefined)?.url ?? '';
            const alreadyOnLogin = window.location.pathname === '/login';
            // /auth/login: the form shows its own error. /auth/me: the route
            // guards (RequireAuth/GuestOnly) handle it via client-side redirect.
            const handledElsewhere =
                requestUrl.includes('/auth/login') || requestUrl.includes('/auth/me');
            if (!handledElsewhere && !alreadyOnLogin) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);