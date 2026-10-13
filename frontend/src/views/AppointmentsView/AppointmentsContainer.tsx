import { useMemo, useState } from "react";
import type { Appointment } from "../../types/appointment";
import { DateNavigation } from "./DateNavigation";
import { AppointmentsFilters } from "./AppointmentsFilters";
import { AppointmentList } from "./AppointmentList";

// mocked data for demonstration purposes
const FAKE_APPOINTMENTS: Appointment[] = [
    { id: 1, client_name: "John Doe", worker_name: "Worker 1", service_name: "Haircut", duration_minutes: 45, start_time: "09:00", appointment_state: "BOOKED" },
    { id: 2, client_name: "Pietro", worker_name: "Worker 2", service_name: "Beard trim", duration_minutes: 30, start_time: "09:30", appointment_state: "BOOKED" },
    { id: 3, client_name: "Marie", worker_name: "Worker 1", service_name: "Haircut", duration_minutes: 45, start_time: "12:30", appointment_state: "COMPLETED" },
    { id: 4, client_name: "Carlos", worker_name: "Worker 3", service_name: "Hair dye", duration_minutes: 90, start_time: "16:00", appointment_state: "CANCELLED" },
];

export function AppointmentsContainer() {
    const [date, setDate] = useState(new Date());
    const [search, setSearch] = useState("");
    const [worker, setWorker] = useState("");
    const [status, setStatus] = useState("");

    const workers = useMemo(
        () => [...new Set(FAKE_APPOINTMENTS.map((a) => a.worker_name))].sort(),
        []
    );

    const filteredAppointments = useMemo(() => {
        const query = search.trim().toLowerCase();
        return FAKE_APPOINTMENTS
            .filter((a) =>
                a.client_name.toLowerCase().includes(query) &&
                (worker === "" || a.worker_name === worker) &&
                (status === "" || a.appointment_state === status)
            )
            .sort((a, b) => a.start_time.localeCompare(b.start_time));
    }, [search, worker, status]);
    
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
            <DateNavigation date={date} onPrevDay={() => changeDay(-1)} onNextDay={() => changeDay(1)} />
            <AppointmentsFilters
                search={search}
                onSearchChange={setSearch}
                worker={worker}
                onWorkerChange={setWorker}
                status={status}
                onStatusChange={setStatus}
                workers={workers}
            />
            <AppointmentList appointments={filteredAppointments} />
        </div>
    );
}
