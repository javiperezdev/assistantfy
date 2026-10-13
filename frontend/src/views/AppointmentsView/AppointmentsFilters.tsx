import { STATE_OPTIONS } from "../../types/appointment";

interface AppointmentsFiltersProps {
    search: string;
    onSearchChange: (value: string) => void;
    worker: string;
    onWorkerChange: (value: string) => void;
    status: string;
    onStatusChange: (value: string) => void;
    workers: string[];
}

const fieldStyles = "px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white text-sm";

export function AppointmentsFilters({ search, onSearchChange, worker, onWorkerChange, status, onStatusChange, workers }: AppointmentsFiltersProps) {
    return (
        <div className="flex flex-col gap-4 sm:flex-row">
            <input
                type="text"
                value={search}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder="Search appointment by client name..."
                className={`${fieldStyles} w-full`}
            />
            <select value={worker} onChange={(e) => onWorkerChange(e.target.value)} className={fieldStyles}>
                <option value="">All workers</option>
                {workers.map((workerName) => (
                    <option key={workerName} value={workerName}>{workerName}</option>
                ))}
            </select>
            <select value={status} onChange={(e) => onStatusChange(e.target.value)} className={fieldStyles}>
                <option value="">All statuses</option>
                {STATE_OPTIONS.map((state) => (
                    <option key={state.value} value={state.value}>{state.label}</option>
                ))}
            </select>
        </div>
    );
}
