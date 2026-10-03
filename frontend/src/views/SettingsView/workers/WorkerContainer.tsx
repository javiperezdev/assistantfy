import { useState } from 'react';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';
import { EditWorkerHoursForm } from './EditWorkerHoursForm';
import type { Worker, WorkerHours } from '../../../types/worker';
import { useCreateWorker, useDeleteWorker, useWorkers } from '../../../hooks/useWorkers';
import { useDeleteWorkerHours, useWorkerHours } from '../../../hooks/useWorkerHours';

export function WorkerContainer() {
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    // Mockup: hours live in local state until the backend exposes worker-hours endpoints
    const [worker, setWorker] = useState<Worker | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const { data: hours, isPending : isHoursPending, isError: isHoursError, refetch: hoursRefetch } = useWorkerHours(worker);    
    const {mutateAsync: deleteWorkerHours} = useDeleteWorkerHours(); // Used mutateAsync to give back a promise and be able to know when the deletion is finished and then change the state of the worker hours list or display an error.
    const {mutate: deleteWorker} = useDeleteWorker();
    const {mutate: createWorker} = useCreateWorker();


    const handleDeleteWorker = (id: number) => {
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

    const handleSaveWorker = (workerName: string) => {
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

    const handleDeleteHours = (workerHours: WorkerHours) : Promise<void> => {
        return deleteWorkerHours(workerHours, {
            onSuccess: () => {
                setToast({message:"Worker hours deleted succesfully!", type:"success"});
            },
            onError: () => {
                setToast({message:"Error occurred when deleting worker hours!", type:"error"});
            }
        })
    }

    const handleSaveHours = (hours: WorkerHours[]) => {
        if (!hours) return;
        if (hours.some(h => h.start_time >= h.end_time)) {
            setToast({message:"Start time must be before end time", type:"error"});
            return;
        }
        setWorker(null);
        setToast({message:"Working hours saved! (mock)", type:"success"});
    }

    const { data: workers, isPending : isWorkerPending, isError: isWorkerError, refetch: workerRefetch } = useWorkers();

    if (isWorkerPending) return <LoadingSpinner message="Loading workers..." size="md" />;
    if (isWorkerError) return <ErrorMessage fullPage message="We couldn't load the workers. Please try again." onRetry={() => workerRefetch()} />;
    
    return (
        <>
            <WorkerCard
                workerList={workers}    
                onDeleteWorker={handleDeleteWorker}
                onAddWorker={handleAddWorker}
                onEditHours={setWorker}
            />

            {isPopUpOpen && (
                <AddWorkerForm onClose={() => setIsPopUpOpen(false)} onSave={(handleSaveWorker)} />)}

            {worker && hours && (
                <EditWorkerHoursForm
                    worker={worker}
                    initialHours={hours}
                    onClose={() => setWorker(null)}
                    onSave={handleSaveHours}
                    onDeleteHour={handleDeleteHours}
                />)}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}

