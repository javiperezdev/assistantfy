import { PopUpTemplate } from '../../../components/PopUpTemplate';
import React, {useState } from 'react'
import { Button } from '../../../components/Button';

interface AddWorkerFormProps {
    onClose: () => void;
    onSave: (name: string) => void;
}

export function AddWorkerForm({ onClose, onSave }: AddWorkerFormProps) {
    const [name, setName] = useState("");

    const handleSubmit = (e: React.SubmitEvent) => {
        e.preventDefault();
        onSave(name);
    }
    
    return (
        <PopUpTemplate title="Add worker" onClose={onClose}>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-2">
                <div className="flex flex-col gap-1">
                    <label className="text-sm font-semibold text-slate-700">
                        Name
                    </label>
                    <input 
                        type="text" 
                        value={name} 
                        onChange={(e) => setName(e.target.value)}
                        className="field-sizing-fixed w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:border-indigo-500 transition-all text-slate-800"
                    />
                </div>
                <Button 
                    onClick={() => onSave} infoMessage="Save worker" 
                >
                    Save worker
                </Button>
            </form>
        </PopUpTemplate>
    );
}