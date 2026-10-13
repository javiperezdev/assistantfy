export type AppointmentState = "BOOKED" | "COMPLETED" | "NO_SHOW" | "CANCELLED";

export const STATE_OPTIONS: { value: AppointmentState; label: string }[] = [
    { value: "BOOKED", label: "Booked" },
    { value: "COMPLETED", label: "Completed" },
    { value: "NO_SHOW", label: "No show" },
    { value: "CANCELLED", label: "Cancelled" },
];

export interface Appointment {
    id: number;
    client_name: string;
    worker_name: string;
    service_name: string;
    duration_minutes: number;
    start_time: string; // "HH:mm"
    appointment_state: AppointmentState;
}
