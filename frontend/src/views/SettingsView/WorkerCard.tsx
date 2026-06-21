import type { Worker } from '../../types/worker';
import { DeleteButton } from '../../components/DeleteButton';


export interface WorkersCardProps {
    workerList: Worker[];
    onDeleteWorker: (id: number) => void;
}

export function WorkerCard({ workerList, onDeleteWorker }: WorkersCardProps) {
    return (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h1 className="text-xl font-bold text-slate-800 mb-4">Workers</h1>
            <div className="space-y-3">
                {workerList.map(({ id, name }) => (
                <div key={id} className="flex items-center justify-between p-3 bg-slate-50 border border-slate-100 rounded-xl">                    <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold text-sm">
                        {name.charAt(0).toUpperCase()}
                    </div> 
                    <span className="text-slate-700 font-medium">{name}</span>
                    <DeleteButton onClick={() => onDeleteWorker(id)} infoMessage={`Delete ${name}`} />
                </div>))}
            </div>
    </div>
    );
}