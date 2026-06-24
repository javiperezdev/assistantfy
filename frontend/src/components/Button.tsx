import type { ReactNode } from 'react'

interface ButtonProps {
    onClick: () => void;
    infoMessage: string;
    children: ReactNode;
    variant?: 'solid' | 'minimal';
}

export function Button({ onClick, infoMessage, children, variant = 'solid' }: ButtonProps) {
    const baseStyles = "text-sm font-medium transition-colors flex items-center justify-center gap-2 rounded transition-all duration-200 cursor-pointer";

    const variantStyles = variant === 'solid'
        ? "h-10 px-4 border border-blue-600 bg-blue-600 text-white hover:bg-blue-700 shadow-sm" 
        : "bg-transparent text-slate-400 hover:text-red-500 hover:bg-slate-100 p-2 stroke-[1.5]"; 

    return (
        <button 
            onClick={onClick} 
            aria-label={infoMessage} 
            title={infoMessage} 
            className={`${baseStyles} ${variantStyles}`}
        >
            {children}
        </button>
    );
}