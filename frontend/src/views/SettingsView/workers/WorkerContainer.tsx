import { useState, useEffect } from 'react';
import type { Worker } from '../../../types/worker';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { getWorkers } from '../../../services/workerService';

export function WorkerContainer() {
    const [workers, setWorkers] = useState<Worker[]>([]);
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

    const handleDeleteWorker = (id: number) => {
        setWorkers(workers.filter(worker => worker.id != id));
    };

    const handleAddWorker = () => {
       setIsPopUpOpen(true);
    }

    // Currently mocking the creation of the worker.

    const handleSaveWorker = (workerName: string) => {
        const newWorker = {
            id: Date.now(),
            business_id: 1,
            name: workerName
        }

        if (workerName.trim() !== "") {
            setWorkers([...workers, newWorker]);
            setToast({message:"Worker added successfully!", type:"success"});
        }

        else {
            setToast({message:"Worker couldn't be added because name is empty!", type:"error"});
        }
    }
    
    useEffect(() => {
        const loadWorkers = async () => {
            const newWorkers = await getWorkers();
            setWorkers(newWorkers);
        }
        
        loadWorkers();
    }, []);

    return (
        <>
            <WorkerCard
                workerList={workers} 
                onDeleteWorker={handleDeleteWorker}
                onAddWorker={handleAddWorker}
            />

            {isPopUpOpen && (
                <AddWorkerForm onClose={() => setIsPopUpOpen(false)} onSave={(handleSaveWorker)} />)}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}

