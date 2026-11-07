import type { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoadingSpinner } from './LoadingSpinner';

function FullPageSpinner() {
    return (
        <div className="min-h-screen flex items-center justify-center">
            <LoadingSpinner message="Loading..." size="md" />
        </div>
    );
}

// Renders children only when there is a valid session; otherwise bounces to /login. 
export function RequireAuth({ children }: { children: ReactNode }) {
    const { isPending, isError } = useAuth();

    if (isPending) return <FullPageSpinner />;
    if (isError) return <Navigate to="/login" replace />;
    return <>{children}</>;
}

// Inverse of RequireAuth: a logged-in user has no business on /login.
export function GuestOnly({ children }: { children: ReactNode }) {
    const { isPending, isError } = useAuth();

    if (isPending) return <FullPageSpinner />;
    if (!isError) return <Navigate to="/" replace />;
    return <>{children}</>;
}
