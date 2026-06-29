import { useState, useEffect } from 'react';
import type { Worker } from '../../../types/worker';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { getWorkers, addWorker, deleteWorker } from '../../../services/workerService';

export function WorkerContainer() {
    const [workers, setWorkers] = useState<Worker[]>([]);
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

    const handleDeleteWorker = async (id: number) => {
        await deleteWorker(id)
        setWorkers(workers.filter(worker => worker.id != id));
        setToast({message:"Worker deleted succesfully!", type:"success"});
    };

    const handleAddWorker = () => {
       setIsPopUpOpen(true);
    }

    const handleSaveWorker = async (workerName: string) => {
        const newWorker = await addWorker(workerName)

        if (workerName.trim() !== "" && newWorker !== undefined) {
            setWorkers([...workers, newWorker]);
            setToast({message:"Worker added successfully!", type:"success"});
        }

        else {
            setToast({message:"Worker couldn't be added, please try again later!", type:"error"});
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

