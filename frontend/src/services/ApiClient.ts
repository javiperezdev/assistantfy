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
            // Don't redirect when the login call itself fails; that error is handled by the form.
            if (!requestUrl.includes('/auth/login') && !alreadyOnLogin) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);