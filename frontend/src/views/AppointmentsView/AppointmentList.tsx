import type { Appointment, AppointmentState } from "../../types/appointment";
import { AppointmentCard } from "./AppointmentCard";

export function AppointmentList({ appointments, onSetState }: {
    appointments: Appointment[];
    onSetState: (id: number, state: AppointmentState) => void;
}) {
    if (appointments.length === 0) {
        return (
            <div className="text-center py-6 text-blue-400 font-medium">
                No appointments found.
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-3">
            {appointments.map((appointment) => (
                <AppointmentCard key={appointment.id} appointment={appointment} onSetState={onSetState} />
            ))}
        </div>
    );
}
