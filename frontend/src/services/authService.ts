import { AxiosError } from 'axios';
import { apiClient } from './ApiClient';

export interface AuthUser {
    email: string;
}

export async function login(email: string, password: string): Promise<AuthUser> {
    try {
        const response = await apiClient.post('/auth/login', { email, password });
        return { email: response.data.user.email };
    } catch (error) {
        const detail =
            error instanceof AxiosError
                ? (error.response?.data as { detail?: string } | undefined)?.detail
                : undefined;
        throw new Error(detail || 'Invalid email or password', { cause: error });
    }
}

// Lets the caller know whether the current session is valid. Errors (401)
// propagate so the caller can tell "authenticated" from "not"; no redirect here.
export async function getMe(): Promise<AuthUser> {
    const response = await apiClient.get('/auth/me');
    return { email: response.data.email };
}
