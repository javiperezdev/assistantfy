import { Button } from './Button';

interface ErrorMessageProps {
    title?: string;
    message?: string;
    onRetry?: () => void;
    fullPage?: boolean;
}

export function ErrorMessage({
    title = 'Something went wrong',
    message,
    onRetry,
    fullPage = false,
}: ErrorMessageProps) {
    return (
        <div className={`flex flex-col items-center justify-center gap-3 px-4 ${fullPage ? 'py-16' : 'py-4'}`}>
            <div className="flex flex-col items-center gap-1">
                <span className="text-sm font-semibold text-red-800">{title}</span>
                {message && (
                    <span className="text-xs font-medium text-red-600 text-center max-w-xs">
                        {message}
                    </span>
                )}
            </div>
            {onRetry && (
                <Button onClick={onRetry} infoMessage="Retry loading">
                    Retry
                </Button>
            )}
        </div>
    );
}