import type { Service } from '../../../types/service';
import type { Worker } from '../../../types/worker';
import { Button } from '../../../components/Button';
import { Trash } from '../../../components/icons/Trash';
import { Plus } from '../../../components/icons/Plus';
import { SettingsCard } from '../../../components/SettingsCard';
import { EditIcon } from '../../../components/icons/EditIcon';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';

export interface ServicesCardProps {
    serviceList: Service[];
    workerList?: Worker[];
    isWorkerError: boolean;
    isWorkerPending: boolean;
    isWorkerServicePending: boolean;
    isWorkerServiceError: boolean;
    assignedWorkersMap: Record<number, number[]>;
    onDeleteService: (id: number, serviceWorkerIds) => void;
    onAddService: () => void;
    onUpdateService: (service: Service, workerIds: number[]) => void;
}

export function ServicesCard({ 
    serviceList, 
    workerList,
    isWorkerError,
    isWorkerPending,
    isWorkerServicePending,
    isWorkerServiceError,
    assignedWorkersMap,
    onDeleteService, 
    onAddService,
    onUpdateService
}: ServicesCardProps) {
    const addServiceButton = (
        <Button 
            onClick={onAddService} infoMessage="Add service"
        >
            <Plus />
            Add new service
        </Button>
    );

    return (
        <SettingsCard title="Services" action={addServiceButton}>
            <div className="space-y-4">
                {serviceList.map((service) => {
                    const id = service.id;
                    const safeWorkerList = workerList ?? [];
                    const serviceWorkerIds = assignedWorkersMap?.[id] ?? [];
                    const serviceWorkers = safeWorkerList.filter(w => w.id !== undefined && serviceWorkerIds.includes(w.id));

                    return (
                        <div key={id} className="flex flex-col gap-3 p-4 bg-blue-50 border border-blue-100 rounded-xl hover:border-blue-200 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex flex-col">
                                    <span className="text-blue-950 font-bold text-base">{service.name}</span>
                                    <span className="text-sm font-medium text-blue-600">${service.price} • {service.duration_minutes} min</span>
                                </div>
                                <div className="flex items-center gap-1">
                                    <Button 
                                        onClick={() => onUpdateService(service, serviceWorkerIds)} 
                                        infoMessage={`Edit ${service.name}`} 
                                        variant='minimal'
                                    >
                                        <EditIcon />
                                    </Button>
                                    <Button 
                                        onClick={() => id !== undefined && onDeleteService(id, serviceWorkerIds)} 
                                        infoMessage={`Delete ${service.name}`} 
                                        variant='minimal'
                                    > 
                                        <Trash />
                                    </Button>
                                </div>
                            </div>

                            <div className="flex flex-col gap-1 border-t border-blue-100/60 pt-2">
                                <span className="text-xs font-semibold uppercase tracking-wider text-blue-500">Assigned Team</span>
                                {(isWorkerPending || isWorkerServicePending) && <LoadingSpinner />}
                                {(isWorkerError || isWorkerServiceError) && <ErrorMessage message="Could not load assigned workers" />}
                                {serviceWorkers.length === 0 ? (
                                    <span className="text-xs text-blue-400 italic">No workers assigned</span>
                                ) : (
                                    <div className="flex flex-wrap gap-2 mt-1">
                                        {serviceWorkers.map((worker) => (
                                            <div key={worker.id} className="flex items-center gap-1.5 px-2 py-1 bg-white border border-blue-200 rounded-lg shadow-sm" title={worker.name}>
                                                <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-[10px]">
                                                    {worker.name.charAt(0).toUpperCase()}
                                                </div>
                                                <span className="text-xs font-medium text-blue-900">{worker.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
                {serviceList.length === 0 && (
                    <div className="text-center py-6 text-blue-400 font-medium">
                        No services registered yet. Click 'Add new service'.
                    </div>
                )}
            </div>
        </SettingsCard>
    );
}
