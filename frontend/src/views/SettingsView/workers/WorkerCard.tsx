import type { Worker } from '../../../types/worker';
import { Button } from '../../../components/Button';
import { Trash } from '../../../components/icons/Trash';
import { Plus } from '../../../components/icons/Plus';
import { EditIcon } from '../../../components/icons/EditIcon';
import { SettingsCard } from '../../../components/SettingsCard';


export interface WorkersCardProps {
    workerList: Worker[];
    onDeleteWorker: (id: number) => void;
    onAddWorker: () => void;
    onEditHours: (worker: Worker) => void;
}

export function WorkerCard({ workerList, onDeleteWorker, onAddWorker, onEditHours }: WorkersCardProps) {
    const addWorkerButton = (
        <Button 
            onClick={onAddWorker} infoMessage="Add worker"
        >
            <Plus />
            Add new worker
        </Button>
    );

    return (
        <SettingsCard title="Workers" action={addWorkerButton}>
            <div className="space-y-3">
                {workerList.map((worker) => (
                <div key={worker.id} className="flex items-center justify-between p-3 bg-blue-50 border border-blue-100 rounded-xl">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-200 text-blue-800 flex items-center justify-center font-semibold text-sm">
                            {worker.name.charAt(0).toUpperCase()}
                        </div> 
                        <span className="text-blue-950 font-medium">{worker.name}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Button onClick={() => onEditHours(worker)} infoMessage={`Edit ${worker.name} working hours`} variant='minimal'>
                            <EditIcon />
                        </Button>
                        <Button onClick={() => worker.id !== undefined && onDeleteWorker(worker.id)} infoMessage={`Delete ${worker.name}`} variant='minimal'> <Trash /></Button>
                    </div>
                </div>))}
                {workerList.length === 0 && (
                    <div className="text-center py-6 text-blue-400 font-medium">
                        No workers registered yet. Click 'Add new worker'.
                    </div>
                )}
            </div>
        </SettingsCard>
    );
}
