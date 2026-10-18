import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createAppointment, getAppointments, updateAppointmentState } from "../services/appointmentService";
import type { Appointment, AppointmentState } from "../types/appointment";

export function useAppointments(date: string) {
    return useQuery<Appointment[]> ({
        queryKey: ['appointments', date],
        queryFn: () => getAppointments(date),
        // Appointments can also be booked through WhatsApp (by the AI), so a
        // plain React Query cache would go stale without any mutation to
        // invalidate it. Polling keeps the owner's agenda fresh on its own.
        // 30s polling — upgrade path: SSE/WebSocket push if real-time ever becomes a hard requirement.
        refetchInterval: 30_000
    });
}

export interface CreateAppointmentInput {
    phone_number: string;
    service_id: number;
    start_time: string;
    name?: string;
    worker_id?: number;
}

export function useCreateAppointment() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (input: CreateAppointmentInput) => createAppointment(
            input.phone_number, input.service_id, input.start_time, input.name, input.worker_id
        ),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['appointments']
            })
        }
    })
}

export function useUpdateAppointmentState() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: ({ appointment_id, new_state }: { appointment_id: number; new_state: AppointmentState }) =>
            updateAppointmentState(appointment_id, new_state),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: ['appointments']
            })
        }
    })
}
