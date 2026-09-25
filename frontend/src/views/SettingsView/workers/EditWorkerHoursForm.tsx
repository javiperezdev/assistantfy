import { useState } from 'react';
import { PopUpTemplate } from '../../../components/PopUpTemplate';
import { Button } from '../../../components/Button';
import { HoursDayList, type DaySlot } from '../../../components/HoursDayList';
import { nextSlotEnd } from '../../../utils/timeSlots';
import type { DayOfWeekValue } from '../../../types/business';
import type { Worker, WorkerHours } from '../../../types/worker';

interface EditWorkerHoursFormProps {
    worker: Worker;
    initialHours: WorkerHours[];
    onClose: () => void;
    onSave: (hours: WorkerHours[]) => void;
}

export function EditWorkerHoursForm({ worker, initialHours, onClose, onSave }: EditWorkerHoursFormProps) {
    const [hours, setHours] = useState<WorkerHours[]>(initialHours);

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

    return (
        <PopUpTemplate title={`Working hours - ${worker.name}`} onClose={onClose}>
            <div className="max-h-[60vh] overflow-y-auto pr-1">
                <HoursDayList
                    slots={hours}
                    onToggleDay={handleToggleDay}
                    onSlotChange={(slot: DaySlot, start_time, end_time) =>
                        setHours(prev => prev.map(h => h === (slot as WorkerHours) ? { ...h, start_time, end_time } : h))}
                    onAddSlot={handleAddSlot}
                    onRemoveSlot={(slot) => setHours(prev => prev.filter(h => h !== (slot as WorkerHours)))}
                />
            </div>
            <Button onClick={() => onSave(hours)} infoMessage={`Save ${worker.name} working hours`}>
                Save hours
            </Button>
        </PopUpTemplate>
    );
}
