import { useMemo, useState } from "react";
import { useAppointments, useCreateAppointment, useUpdateAppointmentState, type CreateAppointmentInput } from "../../hooks/useAppointments";
import type { AppointmentState } from "../../types/appointment";
import { DateNavigation } from "./DateNavigation";
import { AppointmentsFilters } from "./AppointmentsFilters";
import { AppointmentList } from "./AppointmentList";
import { AddAppointmentForm } from "./AddAppointmentForm";
import { Button } from "../../components/Button";
import { Toast } from "../../components/Toast";

// Local date parts, not toISOString(): the latter is UTC and would shift the
// day backwards for timezones behind UTC (e.g. "today" in Spain at 00:30).
function toIsoDate(d: Date): string {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/* The backend sends a human message as `detail` (slot taken, past time,
 * appointment not found...) — show it verbatim in the toast. */
function errorDetail(error: unknown, fallback: string): string {
    const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
    return typeof detail === "string" ? detail : fallback;
}

export function AppointmentsContainer() {
    const [date, setDate] = useState(new Date());
    const [search, setSearch] = useState("");
    const [worker, setWorker] = useState("");
    const [status, setStatus] = useState("");
    const [isPopUpOpen, setIsPopUpOpen] = useState(false);
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

    const { data: appointments = [] } = useAppointments(toIsoDate(date));
    const { mutate: createAppointment } = useCreateAppointment();
    const { mutate: updateAppointmentState } = useUpdateAppointmentState();

    const handleAddAppointment = (input: CreateAppointmentInput) => {
        createAppointment(input, {
            onSuccess: () => {
                setToast({ message: "Appointment booked!", type: "success" });
            },
            onError: (error) => {
                setToast({
                    message: errorDetail(error, "Could not book the appointment"),
                    type: "error",
                });
            },
        });
        setIsPopUpOpen(false);
    };

    const handleSetState = (appointment_id: number, new_state: AppointmentState) => {
        updateAppointmentState({ appointment_id, new_state }, {
            onSuccess: () => {
                setToast({ message: `Appointment marked as ${new_state.toLowerCase().replace("_", " ")}`, type: "success" });
            },
            onError: (error) => {
                setToast({
                    message: errorDetail(error, "Could not update the appointment"),
                    type: "error",
                });
            },
        });
    };

    const workers = useMemo(
        () => [...new Set(appointments.map((a) => a.worker_name))].sort(),
        [appointments]
    );

    /* search/worker/status filtering happens here in the browser
    *  because a single day is a tiny dataset (at least for the business we will have in the MVP) 
    *  this keeps typing instant.
    *  The backend sends the whole day unfiltered (something that it has to do when appointment page is open, so it seems efficient).
    */
    
    const filteredAppointments = useMemo(() => {
        const query = search.trim().toLowerCase();
        return appointments
            .filter((a) =>
                a.client_name.toLowerCase().includes(query) &&
                (worker === "" || a.worker_name === worker) &&
                (status === "" || a.appointment_state === status)
            )
            .sort((a, b) => a.start_time.localeCompare(b.start_time));
    }, [appointments, search, worker, status]); // Dependency array (if something changes it has to do the calculation again)
    
    /*If you click previous or next day, 
    * this function will receive a delta of -1 or 1 respectively.
    * And it will update the date state by adding the delta to the current date.
    * Even in the cases where it's 31 of January and you click next day, 
    * it will correctly update the date to 1 of February, even though the sum it's 32.
    */
    const changeDay = (delta: number) => setDate((prev) => {
        const next = new Date(prev);
        next.setDate(next.getDate() + delta);
        return next;
    });

    return (
        <div className="flex flex-col gap-6">
            <div className="flex flex-col md:flex-row md:justify-between flex-wrap gap-3">
                <DateNavigation date={date} onPrevDay={() => changeDay(-1)} onNextDay={() => changeDay(1)} />
                <Button onClick={() => setIsPopUpOpen(true)} infoMessage="Book a new appointment">
                    + Add appointment
                </Button>
            </div>
            <AppointmentsFilters
                search={search}
                onSearchChange={setSearch}
                worker={worker}
                onWorkerChange={setWorker}
                status={status}
                onStatusChange={setStatus}
                workers={workers}
            />
            <AppointmentList appointments={filteredAppointments} onSetState={handleSetState} />

            {isPopUpOpen && (
                <AddAppointmentForm
                    onClose={() => setIsPopUpOpen(false)}
                    dateISO={toIsoDate(date)}
                    dateLabel={date.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}
                    onSave={handleAddAppointment}
                />
            )}

            {toast && (
                <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
            )}
        </div>
    );
}
