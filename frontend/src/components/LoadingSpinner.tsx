interface LoadingSpinnerProps {
    message?: string;
    size?: 'sm' | 'md';
}

export function LoadingSpinner({ message, size = 'sm' }: LoadingSpinnerProps) {
    const isMd = size === 'md';

    return (
        <div className={`flex flex-col items-center justify-center gap-3 ${isMd ? 'py-16' : 'py-1'}`}>
            <div
                className={`rounded-full border-2 border-blue-200 border-t-blue-600 animate-spin ${
                    isMd ? 'w-8 h-8' : 'w-5 h-5'
                }`}
            />
            {message && (
                <span className={`font-medium text-blue-600 ${isMd ? 'text-sm' : 'text-xs'}`}>
                    {message}
                </span>
            )}
        </div>
    );
}