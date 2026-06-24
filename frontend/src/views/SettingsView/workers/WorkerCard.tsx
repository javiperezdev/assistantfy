import type { Worker } from '../../../types/worker';
import { Button } from '../../../components/Button';
import { Trash } from '../../../components/icons/Trash';
import { Plus } from '../../../components/icons/Plus';


export interface WorkersCardProps {
    workerList: Worker[];
    onDeleteWorker: (id: number) => void;
    onAddWorker: () => void;
}

export function WorkerCard({ workerList, onDeleteWorker, onAddWorker }: WorkersCardProps) {
    return (
        <div className="bg-white rounded-xl border border-blue-200 p-6">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-xl font-bold text-blue-950">Workers</h1>
                <Button 
                    onClick={onAddWorker} infoMessage="Add worker"
                >
                    <Plus />
                    Add Worker
                </Button>
            </div>
            
            <div className="space-y-3">
                {workerList.map(({ id, name }) => (
                <div key={id} className="flex items-center justify-between p-3 bg-blue-50 border border-blue-100 rounded-xl">                    <div className="w-8 h-8 rounded-full bg-blue-200 text-blue-800 flex items-center justify-center font-semibold text-sm">
                        {name.charAt(0).toUpperCase()}
                    </div> 
                    <span className="text-blue-950 font-medium">{name}</span>
                    <Button onClick={() => id !== undefined && onDeleteWorker(id)} infoMessage={`Delete ${name}`} variant='minimal'> <Trash /></Button>
                </div>))}
            </div>
    </div>
    );
}