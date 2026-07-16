import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getBusinessHours, createBusinessHours, updateBusinessHours, deleteBusinessHours } from "../services/businessService";
import type { BusinessHours } from "../types/business";

export function useBusinessHours() {
    return useQuery<BusinessHours[]> ({
        queryKey: ["business-hour"],
        queryFn: getBusinessHours
    });
}

export function useCreateBusinessHours() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (businessHours: BusinessHours) => createBusinessHours(businessHours.day_of_week, businessHours.start_time, businessHours.end_time), 
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["business-hour"]
            });
        }
    });
}

export function useUpdateBusinessHour() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (businessHours: BusinessHours) => updateBusinessHours(businessHours.id, businessHours.day_of_week, businessHours.start_time, businessHours.end_time), 
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["business-hour"]
            });
        }
    });
}

export function useDeleteBusinessHour() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (id: number) => deleteBusinessHours(id),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ["business-hour"]
            });
        }
    });
}

