import { useState } from 'react';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';
import { EditWorkerHoursForm } from './EditWorkerHoursForm';
import type { Worker, WorkerHours } from '../../../types/worker';
import { useCreateWorker, useDeleteWorker, useWorkers } from '../../../hooks/useWorkers';

export function WorkerContainer() {
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [hoursWorker, setHoursWorker] = useState<Worker | null>(null);
    // Mockup: hours live in local state until the backend exposes worker-hours endpoints
    const [hoursByWorker, setHoursByWorker] = useState<Record<number, WorkerHours[]>>({});
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const {mutate: deleteWorker} = useDeleteWorker();
    const {mutate: createWorker} = useCreateWorker();


    const handleDeleteWorker = async (id: number) => {
        deleteWorker(id, {
            onSuccess: () => {
                setToast({message:"Worker deleted succesfully!", type:"success"});
            },
            onError: () => {
                setToast({message:"Error occurred when deleting worker!", type:"error"});
            }
        })
        
    };

    const handleAddWorker = () => {
       setIsPopUpOpen(true);
    }

    const handleSaveWorker = async (workerName: string) => {
        if (workerName !== "") {
            createWorker(workerName, {
                onSuccess: () => {
                    setToast({message:"Worker was added successfully!", type:"success"})
                },
                onError: () => {
                    setToast({message:"An error occurred when saving worker!", type:"error"})
                }
            })
        }
        else {
            setToast({message:"Worker name cannot be empty!", type:"error"})
        }
        setIsPopUpOpen(false)
    }

    const handleSaveHours = (hours: WorkerHours[]) => {
        if (!hoursWorker) return;
        if (hours.some(h => h.start_time >= h.end_time)) {
            setToast({message:"Start time must be before end time", type:"error"});
            return;
        }
        setHoursByWorker(prev => ({ ...prev, [hoursWorker.id!]: hours }));
        setHoursWorker(null);
        setToast({message:"Working hours saved! (mock)", type:"success"});
    }

    const { data: workers, isPending, isError, refetch } = useWorkers();

    if (isPending) return <LoadingSpinner message="Loading workers..." size="md" />;
    if (isError) return <ErrorMessage fullPage message="We couldn't load the workers. Please try again." onRetry={() => refetch()} />;
    
    return (
        <>
            <WorkerCard
                workerList={workers} 
                onDeleteWorker={handleDeleteWorker}
                onAddWorker={handleAddWorker}
                onEditHours={setHoursWorker}
            />

            {isPopUpOpen && (
                <AddWorkerForm onClose={() => setIsPopUpOpen(false)} onSave={(handleSaveWorker)} />)}

            {hoursWorker && (
                <EditWorkerHoursForm
                    worker={hoursWorker}
                    initialHours={hoursByWorker[hoursWorker.id!] ?? []}
                    onClose={() => setHoursWorker(null)}
                    onSave={handleSaveHours}
                />)}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}

