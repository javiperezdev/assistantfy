import { useState } from 'react';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';
import { EditWorkerHoursForm } from './EditWorkerHoursForm';
import type { Worker, WorkerHours } from '../../../types/worker';
import { useCreateWorker, useDeleteWorker, useWorkers } from '../../../hooks/useWorkers';
import { useCreateWorkerHours, useDeleteWorkerHours, usePatchWorkerHoursDay, useUpdateWorkerHours, useWorkerHours } from '../../../hooks/useWorkerHours';

export function WorkerContainer() {
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [worker, setWorker] = useState<Worker | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const { data: hours} = useWorkerHours(worker);    
    const {mutate: deleteWorkerHours} = useDeleteWorkerHours(); 
    const {mutate: deleteWorker} = useDeleteWorker();
    const {mutate: createWorker} = useCreateWorker();
    const {mutate: createWorkerHours} = useCreateWorkerHours();
    const {mutate: patchWorkerHoursDay} = usePatchWorkerHoursDay();
    const {mutate: updateWorkerHours} = useUpdateWorkerHours();


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

    const handleDeleteHours = (workerHours: WorkerHours) => {
        return deleteWorkerHours(workerHours, {
            onSuccess: () => {
                setToast({message:"Worker hours deleted succesfully!", type:"success"});
            },
            onError: () => {
                setToast({message:"Error occurred when deleting worker hours!", type:"error"});
            }
        })
    }

    const handleAddHour = (hour: WorkerHours) => {
        if (!hour) return
        createWorkerHours(hour, {
            onSuccess: () => {
                setToast({message:"Working hours added!", type:"success"})
            },
            onError: () => {
                setToast({message:"Error occurred when adding working hours!", type:"error"})
            }
        })
    }

    const handleToggleDay = (workerHour: WorkerHours) => {
        patchWorkerHoursDay(workerHour, {
            onSuccess: () => {
                setToast({message:"Working hours updated!", type:"success"})
            },
            onError: () => {
                setToast({message:"Error occurred when updating working hours!", type:"error"})
            }
        })
    }

    const handleUpdateHour = (workerHour: WorkerHours) => {
        if (workerHour.start_time >= workerHour.end_time) {
            setToast({ message: "Start time must be before end time", type: "error" });
            return;
        }
        updateWorkerHours(workerHour, {
            onSuccess: () => {
                setToast({message:"Working hours updated!", type:"success"})
            },
            onError: () => {
                setToast({message:"Error occurred when updating working hours!", type:"error"})
            }
        })
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

            {worker && hours && ( // As we mount the EditWorkerHoursForm only when we have a worker and hours, we avoid the error of trying to access hours when they are undefined.
                <EditWorkerHoursForm
                    worker={worker}
                    initialHours={hours ?? []}
                    onClose={() => setWorker(null)}
                    onCreateHour={handleAddHour}
                    onDeleteHour={handleDeleteHours}
                    onToggleDay={handleToggleDay}
                    onUpdateHour={handleUpdateHour}
                />)}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}

