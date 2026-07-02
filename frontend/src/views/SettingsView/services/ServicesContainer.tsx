import { useState } from 'react';
import type { Service } from '../../../types/service';
import { ServicesCard } from './ServicesCard';
import { AddServiceForm } from './AddServiceForm';
import { Toast } from '../../../components/Toast';
import { useWorkers } from '../../../hooks/useWorkers';
import { useServices, useCreateServiceMutation, useDeleteServiceMutation } from '../../../hooks/useServivces';
import { ErrorMessage } from '../../../components/ErrorMessage';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { useCreateWorkerServiceMutation, useDeleteWorkerServiceMutation, useWorkerService } from '../../../hooks/useWorkerService';
import type { WorkerService } from '../../../types/worker';


export function ServicesContainer() {
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [editingService, setEditingService] = useState<{ service: Service, workerIds: number[] } | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const {data: workers, isPending: isWorkerPending, isError: isWorkerError} = useWorkers();
    const {data: services, isPending: isServicePending, isError: isServiceError, refetch} = useServices();
    const {data: workerService, isPending: isWorkerServicePending, isError: isWorkerServiceError} = useWorkerService();
    const { mutate: deleteService} = useDeleteServiceMutation();
    const {mutate: addService} = useCreateServiceMutation();
    const {mutate: addWorkerService} = useCreateWorkerServiceMutation();
    const {mutate: deleteWorkerService} = useDeleteWorkerServiceMutation();

    const handleDeleteService = (serviceId: number, workerIds: number[]) => {
        console.log(workerIds)
        if (workerIds) {
            workerIds.forEach(workerId => {
                const workerService : WorkerService = {
                service_id: serviceId,
                worker_id: workerId
                }
                deleteWorkerService(workerService)            
            });
        }       
        deleteService(serviceId, {
            onSuccess: () => {
                setToast({message: "Service deleted successfully!", type: "success"})
            },
            onError: () => {
                setToast({message: "Error occurred when deleting the service!", type: "error"})
            }
        })
    }

    const handleAddService = () => {
        setIsPopUpOpen(true);
    }

    const handleEditService = (service: Service, workerIds: number[]) => {
        setIsPopUpOpen(true);
        setEditingService({service, workerIds});
    }

    const handleSaveService = async (name: string, price: number, duration: number, workerIds: number[]) => {
        const service : Service  = {
            name: name,
            price: price,
            duration_minutes: duration
        }
        
        await addService(service, {
            onSuccess: (newService) => {
                setToast({message:"Service added successfully!", type:"success"})
                workerIds.forEach(workerId => {
                    const workerService : WorkerService = {
                        service_id: newService.id,
                        worker_id: workerId
                    }

                    addWorkerService(workerService, {
                        onError: () => {
                            setToast({message:"Error occurred when assigning worker to service!", type: "error"})
                        }
                    })
                });
            },
                
            onError: () => {
                setToast({message:"An error occurred when adding saving the service!", type:"error"})
            }
        });
    }

    if (isServicePending) return <LoadingSpinner size="md" message="Loading services..." />
    if (isServiceError) return <ErrorMessage message="Error occurred when loading services!" onRetry={() => refetch()}/>

    return (
        <>
            <ServicesCard
                serviceList={services}
                workerList={workers}
                isWorkerError={isWorkerError}
                isWorkerPending={isWorkerPending}
                isWorkerServicePending={isWorkerServicePending}
                isWorkerServiceError={isWorkerServiceError}
                assignedWorkersMap={workerService}
                onDeleteService={handleDeleteService}
                onAddService={handleAddService}
                onUpdateService={handleEditService}
            />

            {isPopUpOpen && (
                <AddServiceForm 
                    onClose={() => {
                        setIsPopUpOpen(false);
                        setEditingService(null);
                    }} 
                    onSave={handleSaveService}
                    initialService={editingService?.service}
                    initialWorkerIds={editingService?.workerIds}
                    workerList={workers ?? []}
                />
            )}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}
