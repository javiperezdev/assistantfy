import type { ReactNode } from 'react';

interface AuthCardProps {
    title: string;
    children: ReactNode;
}

export function AuthCard({ title, children }: AuthCardProps) {
    return (
        <div className="bg-blue-50 min-h-screen flex items-center justify-center px-6 py-16">
            <div className="bg-white rounded border border-blue-200 p-6 shadow-sm w-full max-w-md mx-auto">
                <div className="flex flex-col items-center gap-1.5 mb-6 text-center">
                    <h1 className="text-3xl font-bold text-blue-950">Assistantfy</h1>
                    <h2 className="text-2xl font-bold text-blue-950">{title}</h2>
                </div>
                {children}
            </div>
        </div>
    );
}
