import { useQuery } from "@tanstack/react-query";
import { getAppointments } from "../services/appointmentService";
import type { Appointment } from "../types/appointment";

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
