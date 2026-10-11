import { PopUpTemplate } from '../../../components/PopUpTemplate';
import { HoursDayList, type DaySlot } from '../../../components/HoursDayList';
import { nextSlotEnd } from '../../../utils/timeSlots';
import type { DayOfWeekValue } from '../../../types/business';
import type { Worker, WorkerHours } from '../../../types/worker';

interface EditWorkerHoursFormProps {
    worker: Worker
    initialHours: WorkerHours[] | undefined // They can be undefined if they are still not loaded from the backend.
    onClose: () => void
    onDeleteHour: (workerHours: WorkerHours) => void
    onCreateHour: (workerHours: WorkerHours) => void
    onToggleDay: (workerHours: WorkerHours) => void
    onUpdateHour: (workerHours: WorkerHours) => void
}

export function EditWorkerHoursForm({ worker, initialHours, onClose, onDeleteHour, onCreateHour, onToggleDay, onUpdateHour }: EditWorkerHoursFormProps) {
    const handleToggleDay = (day: DayOfWeekValue) => { 
        const daySlots = initialHours?.filter(h => h.day_of_week === day) ?? [];
        const isActive = daySlots.length > 0 && daySlots.every(h => h.is_active);
        const workerHours: WorkerHours = {
            worker_id: worker.id!,
            day_of_week: day,
            start_time: "09:00",
            end_time: "17:00",
            is_active: !isActive
        }

        onToggleDay(workerHours)
    }


    const handleAddSlot = (day: DayOfWeekValue) => {
        const daySlots = initialHours?.filter(h => h.day_of_week === day) ?? [];
        const start = daySlots[daySlots.length - 1]?.end_time ?? "09:00";
        const endTime = nextSlotEnd(start);

        if (!endTime) return;

        const workerHour : WorkerHours = {
            worker_id: worker.id!,
            day_of_week: day,
            start_time: start,
            end_time: endTime
        }
        onCreateHour(workerHour)
    }

    /*
    * workerHours is built in real time as slot is a share object 
    * between the HoursDayList (which has no worker_id) and the EditWorkerHoursForm
    */
    const handleRemoveSlot =  (slot: DaySlot) => { 
        const workerHour : WorkerHours = {
            ...slot,
            worker_id: worker.id! 
        }

        onDeleteHour(workerHour);
    }

    const handleSlotChange = (slot: DaySlot, startTime: string, endTime: string) => {
        const workerHour : WorkerHours = {
            ...slot,
            worker_id: worker.id!,
            start_time: startTime,
            end_time: endTime
        }

        onUpdateHour(workerHour);
    }

    return (
        <PopUpTemplate title={`Working hours - ${worker.name}`} onClose={onClose}>
            <div className="max-h-[60vh] overflow-y-auto pr-1">
                <HoursDayList
                    slots={initialHours ?? []}
                    onToggleDay={handleToggleDay}
                    onSlotChange={(slot, startTime, endTime) => {handleSlotChange(slot, startTime, endTime)}}
                    onAddSlot={handleAddSlot}
                    onRemoveSlot={handleRemoveSlot}
                />
            </div>
        </PopUpTemplate>
    );
}
