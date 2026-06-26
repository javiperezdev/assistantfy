import axios from 'axios';
import type { AxiosInstance } from 'axios';

export const apiClient : AxiosInstance = axios.create({
    baseURL: "/API", // backend url (change to .env in production)
    timeout: 5000,                    // Aborts the request if the server takes longer than 5 seconds (prevents freezing)
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});