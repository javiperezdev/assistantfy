import { useState } from 'react';
import { PopUpTemplate } from '../../../components/PopUpTemplate';
import { Button } from '../../../components/Button';
import { HoursDayList, type DaySlot } from '../../../components/HoursDayList';
import { nextSlotEnd } from '../../../utils/timeSlots';
import type { DayOfWeekValue } from '../../../types/business';
import type { Worker, WorkerHours } from '../../../types/worker';

interface EditWorkerHoursFormProps {
    worker: Worker;
    initialHours: WorkerHours[] | undefined; // They can be undefined if they are still not loaded from the backend.
    onClose: () => void;
    onSave: (hours: WorkerHours[]) => void;
    onDeleteHour: (workerHours: WorkerHours) => Promise<void>;
}

export function EditWorkerHoursForm({ worker, initialHours, onClose, onSave, onDeleteHour }: EditWorkerHoursFormProps) {
    const [hours, setHours] = useState<WorkerHours[]>(initialHours ?? []);
    const handleToggleDay = (day: DayOfWeekValue) => setHours(prev =>
        prev.some(h => h.day_of_week === day)
            ? prev.filter(h => h.day_of_week !== day)
            : [...prev, { worker_id: worker.id ?? 0, day_of_week: day, start_time: "09:00", end_time: "17:00" }]
    );

    const handleAddSlot = (day: DayOfWeekValue) => setHours(prev => {
        const start = [...prev].reverse().find(h => h.day_of_week === day)?.end_time ?? "09:00";
        const end_time = nextSlotEnd(start);
        if (!end_time) return prev; // no room before the last selectable slot
        return [...prev, { worker_id: worker.id ?? 0, day_of_week: day, start_time: start, end_time }];
    });

        /* Function is async because I want to know when it's finished.
        * So I can change the state of the worker hours
        */
        const handleRemoveSlot = async (slot: DaySlot) => { 
            const workerHour : WorkerHours = {
                ...slot,
                worker_id: worker.id! 
            }
            try {
                await onDeleteHour(workerHour);
                setHours(prev => prev.filter(h => h !== slot));
            } catch (error) {
                console.error("Error deleting worker hours:", error);
            }
        }
    return (
        <PopUpTemplate title={`Working hours - ${worker.name}`} onClose={onClose}>
            <div className="max-h-[60vh] overflow-y-auto pr-1">
                <HoursDayList
                    slots={hours}
                    onToggleDay={handleToggleDay}
                    onSlotChange={(slot: DaySlot, start_time, end_time) =>
                        setHours(prev => prev.map(h => h === (slot as WorkerHours) ? { ...h, start_time, end_time } : h))}
                    onAddSlot={handleAddSlot}
                    onRemoveSlot={handleRemoveSlot}
                />
            </div>
            <Button onClick={() => onSave(hours)} infoMessage={`Save ${worker.name} working hours`}>
                Save hours
            </Button>
        </PopUpTemplate>
    );
}
