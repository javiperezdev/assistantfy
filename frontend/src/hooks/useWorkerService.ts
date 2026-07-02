import { createWorkerAssignment, deleteWorkerAssignment, getWorkerAssignments } from "../services/workerServiceService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { WorkerService } from "../types/worker";

export function useWorkerService() {
    return useQuery<Record<number, number[]>>({
        queryKey: ['worker-service'],
        queryFn: () => getWorkerAssignments()
    });
}

export function useCreateWorkerServiceMutation() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async(workerService: WorkerService) => createWorkerAssignment(workerService.service_id, workerService.worker_id), 
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['worker-service']
            });
        }
    });
}

export function useDeleteWorkerServiceMutation() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (workerService: WorkerService) => deleteWorkerAssignment(workerService.service_id, workerService.worker_id),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['worker-service']
            });
        } 
    });
}
