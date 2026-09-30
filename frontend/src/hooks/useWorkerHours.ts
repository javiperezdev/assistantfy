import { useQuery } from "@tanstack/react-query";
import { getWorkerHours} from "../services/workerHourService";
import type { WorkerHours, Worker } from "../types/worker";


export function useWorkerHours(worker: Worker | null) {
    return useQuery<WorkerHours[]> ({
        queryKey: ["worker-hours", worker?.id],
        queryFn: () => getWorkerHours(worker!.id!), // We are sure that worker is not null because of the enabled property below
        enabled: worker !== null // This has to be stablished as a worker can be null
    });
}