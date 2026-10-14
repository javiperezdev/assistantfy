import { useMemo, useState } from "react";
import { useAppointments } from "../../hooks/useAppointments";
import { DateNavigation } from "./DateNavigation";
import { AppointmentsFilters } from "./AppointmentsFilters";
import { AppointmentList } from "./AppointmentList";

// Local date parts, not toISOString(): the latter is UTC and would shift the
// day backwards for timezones behind UTC (e.g. "today" in Spain at 00:30).
function toIsoDate(d: Date): string {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function AppointmentsContainer() {
    const [date, setDate] = useState(new Date());
    const [search, setSearch] = useState("");
    const [worker, setWorker] = useState("");
    const [status, setStatus] = useState("");

    const { data: appointments = [] } = useAppointments(toIsoDate(date));

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
    }, [appointments, search, worker, status]);
    
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
