import { useState, useEffect } from 'react';
import type { Service } from '../../../types/service';
import type { Worker } from '../../../types/worker';
import { ServicesCard } from './ServicesCard';
import { AddServiceForm } from './AddServiceForm';
import { Toast } from '../../../components/Toast';
import { getWorkers } from '../../../services/workerService';

export function ServicesContainer() {
    // mocking services
    const [services, setServices] = useState<Service[]>([
        { id: 1, business_id: 1, name: "Premium Haircut", price: 25, duration_minutes: 30 },
        { id: 2, business_id: 1, name: "Luxury Shave & Facial", price: 40, duration_minutes: 45 },
        { id: 3, business_id: 1, name: "Beard Grooming", price: 15, duration_minutes: 20 }
    ]);

    const [assignedWorkers, setAssignedWorkers] = useState<Record<number, number[]>>({
        1: [1, 2],
        2: [2],
        3: [1]
    });

    const [workers, setWorkers] = useState<Worker[]>([]);
    const [isPopUpOpen, setIsPopUpOpen] = useState<boolean>(false);
    const [editingService, setEditingService] = useState<{ service: Service; workerIds: number[] } | null>(null);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        const loadWorkers = async () => {
            try {
                const fetchedWorkers = await getWorkers();
                setWorkers(fetchedWorkers);
            } catch {
                setWorkers([]);
            }
        };
        
        loadWorkers();
    }, []);

    const handleDeleteService = (id: number) => {
        setServices(services.filter(s => s.id !== id));
        const newAssignments = { ...assignedWorkers };
        delete newAssignments[id];
        setAssignedWorkers(newAssignments);
        setToast({ message: "Service deleted successfully!", type: "success" });
    };

    const handleAddService = () => {
        setEditingService(null);
        setIsPopUpOpen(true);
    };

    const handleEditService = (service: Service, workerIds: number[]) => {
        setEditingService({ service, workerIds });
        setIsPopUpOpen(true);
    };

    const handleSaveService = (name: string, price: number, duration: number, workerIds: number[]) => {
        if (name.trim() === "") {
            setToast({ message: "Service couldn't be saved because name is empty!", type: "error" });
            return;
        }

        if (editingService) {
            const updatedId = editingService.service.id;
            if (updatedId !== undefined) {
                setServices(services.map(s => s.id === updatedId ? { ...s, name, price, duration_minutes: duration } : s));
                setAssignedWorkers({
                    ...assignedWorkers,
                    [updatedId]: workerIds
                });
                setToast({ message: "Service updated successfully!", type: "success" });
            }
        } else {
            const nextId = services.length > 0 ? Math.max(...services.map(s => s.id || 0)) + 1 : 1;
            const newService: Service = {
                id: nextId,
                business_id: 1,
                name,
                price,
                duration_minutes: duration
            };
            setServices([...services, newService]);
            setAssignedWorkers({
                ...assignedWorkers,
                [nextId]: workerIds
            });
            setToast({ message: "Service added successfully!", type: "success" });
        }
        setIsPopUpOpen(false);
        setEditingService(null);
    };

    return (
        <>
            <ServicesCard
                serviceList={services}
                workerList={workers}
                assignedWorkersMap={assignedWorkers}
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
                    workerList={workers}
                />
            )}
        
            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />    
            )}
        </>
    );
}
