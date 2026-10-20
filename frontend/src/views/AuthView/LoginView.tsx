import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthCard } from './AuthCard';
import { login } from '../../services/authService';
import { ErrorMessage } from '../../components/ErrorMessage';

export function LoginView() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.SubmitEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            await login(email, password);
            navigate('/', { state: { welcomeEmail: email } });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthCard title="Sign in">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                    <label htmlFor="email" className="text-sm font-semibold text-blue-950">
                        Email
                    </label>
                    <input
                        id="email"
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="admin@assistantfy.com"
                        className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white"
                    />
                </div>

                <div className="flex flex-col gap-1.5">
                    <label htmlFor="password" className="text-sm font-semibold text-blue-950">
                        Password
                    </label>
                    <input
                        id="password"
                        type="password"
                        required
                        minLength={6}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••"
                        className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white"
                    />
                </div>

                {error && <ErrorMessage title="Login failed" message={error} />}

                <button
                    type="submit"
                    disabled={loading}
                    className="h-10 px-4 border border-blue-600 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
                >
                    {loading ? "Signing in..." : "Sign in"}
                </button>
            </form>

            <p className="mt-4 text-center text-xs text-blue-400 italic">
                Demo credentials: admin@assistantfy.com / password123
            </p>
        </AuthCard>
    );
}
