import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createWorkerHour, deleteWorkerHours, getWorkerHours, patchWorkerHoursDay, putWorkerHours} from "../services/workerHourService";
import type { WorkerHours, Worker } from "../types/worker";


export function useWorkerHours(worker: Worker | null) {
    return useQuery<WorkerHours[]> ({
        queryKey: ["worker-hours", worker?.id],
        queryFn: () => getWorkerHours(worker!.id!), // We are sure that worker is not null because of the enabled property below
        enabled: worker !== null // This has to be stablished as a worker can be null
    })
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
    })
}

export function useCreateWorkerHours() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (workerHours: WorkerHours) => createWorkerHour(workerHours.worker_id!, workerHours.day_of_week, workerHours.start_time, workerHours.end_time),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["worker-hours"]
            })
        }
    })
}

export function usePatchWorkerHoursDay() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (workerHours: WorkerHours) => patchWorkerHoursDay(workerHours.worker_id!, workerHours.day_of_week, workerHours.is_active!),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["worker-hours"]
            })
        }
    })
}

export function useUpdateWorkerHours() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (workerHours: WorkerHours) => putWorkerHours(workerHours.id!,workerHours.worker_id!, workerHours.day_of_week, workerHours.start_time, workerHours.end_time),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["worker-hours"]
            })
        }
    })
}

