import type { Appointment, AppointmentState } from "../../types/appointment";
import { STATE_OPTIONS } from "../../types/appointment";

const STATE_BADGE: Record<AppointmentState, string> = {
    BOOKED: "bg-blue-100 text-blue-700",
    COMPLETED: "bg-green-100 text-green-700",
    NO_SHOW: "bg-amber-100 text-amber-700",
    CANCELLED: "bg-red-100 text-red-700",
};

/* Which states each row offers, as a correction menu: a BOOKED one can become
 * anything, a COMPLETED/NO_SHOW can be corrected, and a CANCELLED is the end
 * of the road (a rebooking is a new appointment, so no control at all).
 */
const STATE_TARGETS: Record<AppointmentState, AppointmentState[]> = {
    BOOKED: ["BOOKED", "COMPLETED", "NO_SHOW", "CANCELLED"],
    COMPLETED: ["COMPLETED", "NO_SHOW", "CANCELLED"],
    NO_SHOW: ["NO_SHOW", "COMPLETED", "CANCELLED"],
    CANCELLED: [],
};

function formatTime(time: string): string {
    const [hours, minutes] = time.split(":").map(Number);
    const suffix = hours >= 12 ? "PM" : "AM";
    return `${hours % 12 || 12}:${String(minutes).padStart(2, "0")} ${suffix}`;
}

export function AppointmentCard({ appointment, onSetState }: {
    appointment: Appointment;
    onSetState: (id: number, state: AppointmentState) => void;
}) {
    const targets = STATE_TARGETS[appointment.appointment_state];
    const badgeClasses = `px-2.5 py-1 rounded-lg text-xs font-semibold shrink-0 ${STATE_BADGE[appointment.appointment_state]}`;


    return (
        <div className="flex flex-col gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl hover:border-blue-200 transition-colors md:flex-row md:items-center md:gap-6 md:p-4">
            <span className="text-blue-950 font-semibold md:w-20 md:shrink-0">
                {formatTime(appointment.start_time)}
            </span>

            <div className="flex flex-col min-w-0 md:flex-1">
                <span className="text-blue-950 font-semibold">
                    {appointment.client_name}
                </span>
                <span className="text-sm font-medium text-blue-600">
                    {appointment.service_name} • {appointment.duration_minutes} min
                </span>
            </div>

            {targets.length === 0 ? (
                <span className={badgeClasses}>Cancelled</span>
            ) : (
                <span className="relative inline-flex shrink-0 self-start md:self-center">
                    <select
                        value={appointment.appointment_state}
                        onChange={(e) =>
                            onSetState(
                                appointment.id,
                                e.target.value as AppointmentState
                            )
                        }
                        aria-label={`State of ${appointment.client_name}'s appointment`}
                        className={`${badgeClasses} appearance-none cursor-pointer pr-6`}
                    >
                        {STATE_OPTIONS.filter((option) =>
                            targets.includes(option.value)
                        ).map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                    <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-[10px] opacity-70">
                        ▾
                    </span>
                </span>
            )}
        </div>
    );
}
