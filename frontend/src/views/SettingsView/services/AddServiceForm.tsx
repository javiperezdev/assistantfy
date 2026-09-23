import { PopUpTemplate } from '../../../components/PopUpTemplate';
import React, { useState } from 'react';
import { Button } from '../../../components/Button';
import type { Service } from '../../../types/service';
import type { Worker } from '../../../types/worker';

interface AddServiceFormProps {
    onClose: () => void;
    onSave: (name: string, price: number, duration: number, workerIds: number[]) => void;
    initialService?: Service;
    initialWorkerIds?: number[];
    workerList: Worker[];
}

export function AddServiceForm({ onClose, onSave, initialService, initialWorkerIds = [], workerList }: AddServiceFormProps) {
    const [name, setName] = useState(initialService?.name || "");
    const [price, setPrice] = useState<string>(initialService?.price !== undefined ? String(initialService.price) : "");
    const [duration, setDuration] = useState<string>(initialService?.duration_minutes !== undefined ? String(initialService.duration_minutes) : "30");
    const [selectedWorkers, setSelectedWorkers] = useState<number[]>(initialWorkerIds);

    // It makes any type conversion to boolean 
    const isEdit = !!initialService;

    const handleSubmit = (e: React.SubmitEvent) => {
        e.preventDefault();
        const numericPrice = parseFloat(price) || 0;
        const numericDuration = parseInt(duration, 10) || 30;
        onSave(name, numericPrice, numericDuration, selectedWorkers);
    };

    const toggleWorker = (workerId: number) => {
        if (selectedWorkers.includes(workerId)) {
            setSelectedWorkers(selectedWorkers.filter(id => id !== workerId));
        } else {
            setSelectedWorkers([...selectedWorkers, workerId]);
        }
    };

    return (
        <PopUpTemplate title={isEdit ? "Update Service" : "Add Service"} onClose={onClose}>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-2">
                <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-semibold text-blue-950">
                        Service Name
                    </label>
                    <input 
                        type="text" 
                        required
                        value={name} 
                        onChange={(e) => setName(e.target.value)}
                        placeholder="e.g. Premium Haircut"
                        className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                        <label className="text-sm font-semibold text-blue-950">
                            Price ($)
                        </label>
                        <input 
                            type="number" 
                            required
                            min="0"
                            step="0.01"
                            value={price} 
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="25.00"
                            className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white"
                        />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <label className="text-sm font-semibold text-blue-950">
                            Duration (min)
                        </label>
                        <input 
                            type="number" 
                            required
                            min="1"
                            value={duration} 
                            onChange={(e) => setDuration(e.target.value)}
                            placeholder="30"
                            className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-semibold text-blue-950">
                        Assign Workers
                    </label>
                    <div className="border border-blue-100 rounded-lg p-3 bg-blue-50/50 max-h-40 overflow-y-auto space-y-2">
                        {workerList.length === 0 ? (
                            <span className="text-xs text-blue-400 italic">No workers available. Add workers in the configurations panel.</span>
                        ) : (
                            workerList.map((worker) => {
                                const isChecked = worker.id !== undefined && selectedWorkers.includes(worker.id);
                                return (
                                    <label key={worker.id} className="flex items-center gap-2.5 cursor-pointer select-none">
                                        <input 
                                            type="checkbox"
                                            checked={isChecked}
                                            onChange={() => worker.id !== undefined && toggleWorker(worker.id)}
                                            className="w-4 h-4 rounded border-blue-200 text-blue-600 focus:ring-blue-500"
                                        />
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[10px]">
                                                {worker.name.charAt(0).toUpperCase()}
                                            </div>
                                            <span className="text-sm text-blue-950 font-medium">{worker.name}</span>
                                        </div>
                                    </label>
                                );
                            })
                        )}
                    </div>
                </div>

                <div className="mt-2">
                    <Button 
                        onClick={() => {}} infoMessage={isEdit ? "Update service details" : "Create new service"} 
                    >
                        {isEdit ? "Update Service" : "Save Service"}
                    </Button>
                </div>
            </form>
        </PopUpTemplate>
    );
}
