import type { ReactNode } from 'react';
import { Button } from './Button';
import { CloseIcon } from './icons/CloseIcon';

interface PopUpTemplateProps {
    title: string;
    onClose: () => void;
    children: ReactNode; 
}

export function PopUpTemplate({ title, onClose, children }: PopUpTemplateProps) {
    return (
        /* Outer frame overlay viewport */
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            
            {/* Transparent Backdrop with click-to-close */}
            <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
            
            {/* White Card Body Frame */}
            <div className="relative bg-white w-full max-w-md rounded-2xl shadow-xl border border-slate-100 p-6 z-10 flex flex-col gap-4">
                
                {/* Header */}
                <div className="flex items-center justify-between border-b border-slate-50 pb-3">
                    <h2 className="text-xl font-bold text-slate-800">{title}</h2>
                    <Button onClick={onClose} infoMessage="Close pop up" variant="minimal">
                        <CloseIcon />
                    </Button>
                </div>

                {/* Custom content */}
                {children}
                
            </div>
        </div>
    );
}