import type { DayOfWeekValue } from '../types/business';
import { TIME_SLOTS, nextSlotEnd } from '../utils/timeSlots';
import { Button } from './Button';
import { CloseIcon } from './icons/CloseIcon';

const DAY_LABELS: Record<DayOfWeekValue, string> = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
};

function displayTime(t: string): string {
    const [hh, mm] = t.split(":").map(Number);
    const p = hh < 12 ? "AM" : "PM";
    const h = hh === 0 ? 12 : hh > 12 ? hh - 12 : hh;
    return mm === 0 ? `${h} ${p}` : `${h}:${String(mm).padStart(2, "0")} ${p}`;
}

export interface DaySlot {
    id?: number;
    day_of_week: number;
    start_time: string;
    end_time: string;
}

export interface HoursDayListProps {
    slots: DaySlot[];
    onToggleDay: (day: DayOfWeekValue) => void;
    onSlotChange: (slot: DaySlot, startTime: string, endTime: string) => void;
    onAddSlot: (day: DayOfWeekValue) => void;
    onRemoveSlot: (slot: DaySlot) => void;
}

export function HoursDayList({ slots, onToggleDay, onSlotChange, onAddSlot, onRemoveSlot }: HoursDayListProps) {
    const slotsByDay = slots.reduce((acc, slot) => {
        (acc[slot.day_of_week as DayOfWeekValue] ??= []).push(slot);
        return acc;
    }, {} as Record<DayOfWeekValue, DaySlot[]>);

    return (
        <div className="flex flex-col gap-2">
            {([1, 2, 3, 4, 5, 6, 7] as DayOfWeekValue[]).map((day) => {
                const daySlots = slotsByDay[day] || [];
                const isClosed = daySlots.length === 0;

                return (
                    <div key={day} className={`flex flex-col p-3 rounded-xl border transition-colors ${isClosed ? "bg-white border-blue-100" : "bg-white border-blue-200"}`}>
                        <div className="flex items-center justify-between">
                            <span className={`text-base font-semibold ${isClosed ? "text-blue-400" : "text-blue-950"}`}>
                                {DAY_LABELS[day]}
                            </span>
                            <button
                                type="button"
                                onClick={() => onToggleDay(day)}
                                className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors cursor-pointer ${isClosed ? "bg-blue-200" : "bg-blue-600"}`}
                            >
                                <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${isClosed ? "translate-x-1" : "translate-x-6"}`} />
                            </button>
                        </div>
                        {!isClosed && (
                            <div className="flex flex-col gap-1.5 mt-2">
                                {daySlots.map((slot, index) => (
                                    <div key={slot.id ?? index} className="flex items-center gap-2">
                                        <select
                                            value={slot.start_time}
                                            onChange={(e) => onSlotChange(slot, e.target.value, slot.end_time)}
                                            className="flex-1 min-w-0 px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 cursor-pointer focus:outline-none focus:border-blue-500"
                                        >
                                            {TIME_SLOTS.map((t) => (
                                                <option key={t} value={t}>{displayTime(t)}</option>
                                            ))}
                                        </select>
                                        <span className="text-blue-300 text-xs shrink-0">to</span>
                                        <select
                                            value={slot.end_time}
                                            onChange={(e) => onSlotChange(slot, slot.start_time, e.target.value)}
                                            className="flex-1 min-w-0 px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 cursor-pointer focus:outline-none focus:border-blue-500"
                                        >
                                            {TIME_SLOTS.map((t) => (
                                                <option key={t} value={t}>{displayTime(t)}</option>
                                            ))}
                                        </select>
                                        <Button
                                            infoMessage="Remove time period"
                                            onClick={() => onRemoveSlot(slot)}
                                            variant="minimal"
                                        >
                                            <CloseIcon/>
                                        </Button>
                                    </div>
                                ))}
                                {nextSlotEnd(daySlots[daySlots.length - 1].end_time) && (
                                    <Button
                                        variant="solid"
                                        onClick={() => onAddSlot(day)}
                                        infoMessage="Add a new time period"
                                    >
                                        + Add time period
                                    </Button>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
