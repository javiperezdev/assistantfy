import { useState } from 'react';
import type { Worker } from '../../types/worker';
import { WorkerCard } from './WorkerCard';

// Mocked data that represents an array of workers 
const workersMock: Worker[] = [
    {id: 1, business_id: 1, name: "Javi Perez"},
    {id: 2, business_id: 1, name: "Joseph Graha"}
    ]

export function WorkerContainer() {
    const [workers, setWorkers] = useState<Worker[]>(workersMock);

    const handleDeleteWorker = (id: number) => {
        setWorkers(workers.filter(worker => worker.id != id));
    };

    return (
        <WorkerCard
            workerList={workers} 
            onDeleteWorker={handleDeleteWorker}
        />
    );
}

