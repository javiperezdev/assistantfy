export interface AuthUser {
    token: string;
    email: string;
}

const DEMO_EMAIL = "admin@assistantfy.com";
const DEMO_PASSWORD = "password123";

// mock auth, swap for a real API call when the backend exists
export function login(email: string, password: string): Promise<AuthUser> {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (email === DEMO_EMAIL && password === DEMO_PASSWORD) {
                resolve({ token: "mock-token", email });
            } else {
                reject(new Error("Invalid email or password"));
            }
        }, 800);
    });
}
