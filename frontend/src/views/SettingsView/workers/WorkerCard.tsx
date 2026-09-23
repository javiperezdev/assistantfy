import type { Worker } from '../../../types/worker';
import { Button } from '../../../components/Button';
import { Trash } from '../../../components/icons/Trash';
import { Plus } from '../../../components/icons/Plus';
import { SettingsCard } from '../../../components/SettingsCard';


export interface WorkersCardProps {
    workerList: Worker[];
    onDeleteWorker: (id: number) => void;
    onAddWorker: () => void;
}

export function WorkerCard({ workerList, onDeleteWorker, onAddWorker }: WorkersCardProps) {
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
                {workerList.map(({ id, name }) => (
                <div key={id} className="flex items-center justify-between p-3 bg-blue-50 border border-blue-100 rounded-xl">                    <div className="w-8 h-8 rounded-full bg-blue-200 text-blue-800 flex items-center justify-center font-semibold text-sm">
                        {name.charAt(0).toUpperCase()}
                    </div> 
                    <span className="text-blue-950 font-medium">{name}</span>
                    <Button onClick={() => id !== undefined && onDeleteWorker(id)} infoMessage={`Delete ${name}`} variant='minimal'> <Trash /></Button>
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