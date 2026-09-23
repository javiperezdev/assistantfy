import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getServices, deleteService, createService  } from "../services/serviceService";
import type { Service } from "../types/service";

export function useServices() {
    return useQuery<Service[]> ({
        queryKey: ['services'],
        queryFn: getServices
    });
}

export function useDeleteServiceMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (serviceId: number) => deleteService(serviceId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['services']
            });
        }
    });
}

export function useCreateServiceMutation() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: async (service: Service) => {
            const newService = await createService(service.name, service.price, service.duration_minutes);
            return newService;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['services']
            });
        }
    });
}