import type { ReactNode } from 'react';

interface SettingsCardProps {
    title?: string;
    action?: ReactNode;
    children: ReactNode;
    isPlaceholder?: boolean;
}

export function SettingsCard({ title, action, children, isPlaceholder = false }: SettingsCardProps) {
    if (isPlaceholder) {
        return (
            <div className="bg-white rounded-xl border border-blue-200 border-dashed p-6 text-center text-blue-400 min-h-[150px] flex items-center justify-center">
                {children}
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl border border-blue-200 p-6">
            {(title || action) && (
                <div className="flex items-center justify-between mb-4">
                    {title && <h1 className="text-xl font-bold text-blue-950">{title}</h1>}
                    {action && <div>{action}</div>}
                </div>
            )}
            {children}
        </div>
    );
}
