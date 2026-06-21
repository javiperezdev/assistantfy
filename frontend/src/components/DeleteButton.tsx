interface DeleteButtonProps {
    onClick: () => void;
    infoMessage: string;
}

export function DeleteButton({ onClick, infoMessage } : DeleteButtonProps) {
    return (
        <button onClick={onClick} aria-label={infoMessage} className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all">
            <svg 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                strokeWidth={1.25} 
                stroke="currentColor" 
                className="w-5 h-5"
                >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 6h15M9 6V4.5a1.5 1.5 0 0 1 1.5-1.5h3a1.5 1.5 0 0 1 1.5 1.5V6" />          
                <path strokeLinecap="round" strokeLinejoin="round" d="M18.5 6v12.5a2.5 2.5 0 0 1-2.5 2.5H8a2.5 2.5 0 0 1-2.5-2.5V6" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 10v6M14 10v6" />
            </svg>
        </button>
    );
}