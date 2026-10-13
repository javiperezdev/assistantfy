import type { Appointment, AppointmentState } from "../../types/appointment";
import { STATE_OPTIONS } from "../../types/appointment";

const STATE_LABEL = Object.fromEntries(
    STATE_OPTIONS.map(({ value, label }) => [value, label])
) as Record<AppointmentState, string>;

const STATE_BADGE: Record<AppointmentState, string> = {
    BOOKED: "bg-blue-100 text-blue-700",
    COMPLETED: "bg-green-100 text-green-700",
    NO_SHOW: "bg-amber-100 text-amber-700",
    CANCELLED: "bg-red-100 text-red-700",
};

function formatTime(time: string): string {
    const [hours, minutes] = time.split(":").map(Number);
    const suffix = hours >= 12 ? "PM" : "AM";
    return `${hours % 12 || 12}:${String(minutes).padStart(2, "0")} ${suffix}`;
}

export function AppointmentCard({ appointment }: { appointment: Appointment }) {
    return (
        <div className="flex items-center gap-4 p-4 bg-blue-50 border border-blue-100 rounded-xl hover:border-blue-200 transition-colors">
            <span className="text-blue-950 font-semibold w-20 shrink-0">
                {formatTime(appointment.start_time)}
            </span>
            <div className="flex flex-col flex-1 min-w-0">
                <span className="text-blue-950 font-bold text-base truncate">{appointment.client_name}</span>
                <span className="text-sm font-medium text-blue-600">
                    {appointment.service_name} • {appointment.duration_minutes} min
                </span>
            </div>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold shrink-0 ${STATE_BADGE[appointment.appointment_state]}`}>
                {STATE_LABEL[appointment.appointment_state]}
            </span>
        </div>
    );
}
