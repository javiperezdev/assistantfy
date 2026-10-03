import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteWorkerHours, getWorkerHours} from "../services/workerHourService";
import type { WorkerHours, Worker } from "../types/worker";


export function useWorkerHours(worker: Worker | null) {
    return useQuery<WorkerHours[]> ({
        queryKey: ["worker-hours", worker?.id],
        queryFn: () => getWorkerHours(worker!.id!), // We are sure that worker is not null because of the enabled property below
        enabled: worker !== null // This has to be stablished as a worker can be null
    });
}

export function useDeleteWorkerHours() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (workerHours: WorkerHours) => deleteWorkerHours(workerHours.id!, workerHours.worker_id!),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["worker-hours"]
            });
        }
    });
}