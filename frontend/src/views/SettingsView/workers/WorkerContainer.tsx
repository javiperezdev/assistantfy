import { useState } from 'react';
import { WorkerCard } from './WorkerCard';
import { AddWorkerForm } from './AddWorkerForm';
import { Toast } from '../../../components/Toast';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';
import { useCreateWorker, useDeleteWorker, useWorkers } from '../../../hooks/useWorkers';

export function WorkerContainer() {
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
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

    const { data: workers, isPending, isError, refetch } = useWorkers();

    if (isPending) return <LoadingSpinner message="Loading workers..." size="md" />;
    if (isError) return <ErrorMessage fullPage message="We couldn't load the workers. Please try again." onRetry={() => refetch()} />;
    
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

