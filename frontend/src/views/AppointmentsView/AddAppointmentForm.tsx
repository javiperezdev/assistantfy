import React, { useState } from 'react';
import { PopUpTemplate } from '../../components/PopUpTemplate';
import { Button } from '../../components/Button';
import { useServices } from '../../hooks/useServivces';
import { useWorkers } from '../../hooks/useWorkers';
import { useWorkerService } from '../../hooks/useWorkerService';
import type { CreateAppointmentInput } from '../../hooks/useAppointments';
import { TIME_SLOTS } from '../../utils/timeSlots';

interface AddAppointmentFormProps {
    onClose: () => void;
    /** The day the agenda is currently showing (YYYY-MM-DD, local date parts). */
    dateISO: string;
    /** label of that day, shown so the owner knows where this lands. */
    dateLabel: string;
    onSave: (input: CreateAppointmentInput) => void;
}

export function AddAppointmentForm({ onClose, dateISO, dateLabel, onSave }: AddAppointmentFormProps) {
    const [phone, setPhone] = useState("");
    const [name, setName] = useState("");
    const [serviceId, setServiceId] = useState("");
    const [workerId, setWorkerId] = useState(""); 
    const [timeSlot, setTimeSlot] = useState("");

    const { data: services = [] } = useServices();
    const { data: workers = [] } = useWorkers();
    const { data: workerService } = useWorkerService();

    /* Worker assignments arrive as { service_id: [worker_id] }, so once a
     * service is chosen only the workers that can perform it are offered.
     * Backend validation still backstops a service with no assignments. */
    const assignableIds = serviceId ? (workerService as Record<number, number[]>)?.[Number(serviceId)] : undefined;
    const visibleWorkers = Array.isArray(assignableIds)
        ? workers.filter((w) => w.id !== undefined && assignableIds.includes(w.id))
        : workers;

    const handleSubmit = (e: React.SubmitEvent) => {
        e.preventDefault();
        onSave({
            phone_number: phone.trim(),
            service_id: Number(serviceId),
            start_time: `${dateISO}T${timeSlot}:00`,
            name: name.trim() || undefined,
            worker_id: workerId ? Number(workerId) : undefined,
        });
    };

    const inputStyles = "w-full px-3 py-2 border border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 transition-all text-blue-950 bg-white";
    const labelStyles = "text-sm font-semibold text-blue-950";

    return (
        <PopUpTemplate title="Add Appointment" onClose={onClose}>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-2">
                <p className="text-sm text-blue-400 -mb-2">Booking for {dateLabel}</p>

                <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                        <label className={labelStyles}>Phone Number</label>
                        <input
                            type="tel"
                            required
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            placeholder="e.g. 34665940297"
                            className={inputStyles}
                        />
                    </div>
                    <div className="flex flex-col gap-1.5">
                        <label className={labelStyles}>Client Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g. María López"
                            className={inputStyles}
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5">
                    <label className={labelStyles}>Service</label>
                    <select required value={serviceId} onChange={(e) => setServiceId(e.target.value)} className={inputStyles}>
                        <option value="" disabled>Select a service</option>
                        {services.map((service) => (
                            <option key={service.id} value={service.id}>
                                {service.name} ({service.duration_minutes} min)
                            </option>
                        ))}
                    </select>
                </div>

                <div className="flex flex-col gap-1.5">
                    <label className={labelStyles}>Worker</label>
                    <select value={workerId} onChange={(e) => setWorkerId(e.target.value)} className={inputStyles}>
                        <option value="">Any worker </option>
                        {visibleWorkers.map((w) => (
                            <option key={w.id} value={w.id}>{w.name}</option>
                        ))}
                    </select>
                </div>

                <div className="flex flex-col gap-1.5">
                    <label className={labelStyles}>Time</label>
                    <select required value={timeSlot} onChange={(e) => setTimeSlot(e.target.value)} className={inputStyles}>
                        <option value="" disabled>Select a time</option>
                        {TIME_SLOTS.map((slot) => (
                            <option key={slot} value={slot}>{slot}</option>
                        ))}
                    </select>
                </div>

                <div className="mt-2">
                    <Button onClick={() => {}} infoMessage="Book this appointment">
                        Book Appointment
                    </Button>
                </div>
            </form>
        </PopUpTemplate>
    );
}
