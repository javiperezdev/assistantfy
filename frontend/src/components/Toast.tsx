import { useEffect } from 'react'
import { Button } from './Button'
import { CloseIcon } from './icons/CloseIcon'

interface ToastProps {
    message: string;
    onClose: () => void;
    type?: 'success' | 'error';
}

export function Toast({ message, onClose, type = 'success' } : ToastProps) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose()
        }, 3000)
        return () => clearTimeout(timer)
    }, [onClose])

    const styles = type === 'success'
        ? {
            container: "bg-white border-l-4 border-l-green-500",
            icon: "text-green-500",
            text: "text-slate-800"
          }
        : {
            container: "bg-white border-l-4 border-l-red-500",
            icon: "text-red-500",
            text: "text-slate-800"
          };

    return (
        <div className={`fixed top-4 right-4 z-50 flex items-center justify-between gap-4 rounded-lg border border-slate-200 p-4 shadow-xl min-w-[320px] max-w-sm animate-fade-in-up ${styles.container}`}>
            <div className="flex items-center gap-3">
                {type === 'success' ? (
                    <svg className={`size-6 ${styles.icon}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                ) : (
                    <svg className={`size-6 ${styles.icon}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                )}
                <span className={`text-sm font-medium ${styles.text}`}>{message}</span>
            </div>
            <Button onClick={onClose} infoMessage="Close notification" variant="minimal">
                <CloseIcon />
            </Button>
        </div>
    );
}