import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { addWorker, deleteWorker, getWorkers } from '../services/workerService';
import type { Worker } from '../types/worker';

export function useWorkers() {
    return useQuery<Worker[]>({
        queryKey: ['workers'],
        queryFn: getWorkers
    });
}

export function useDeleteWorker() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (workerId: number) => deleteWorker(workerId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['workers']
            });
        }
    });
}

export function useCreateWorker() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (name: string) => addWorker(name),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['workers']
            });
        }
    });
}


