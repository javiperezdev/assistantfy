import type { BusinessHours, DayOfWeekValue } from '../../../types/business';
import { SettingsCard } from '../../../components/SettingsCard';
import { Button } from '../../../components/Button';
import { CloseIcon } from '../../../components/icons/CloseIcon';

const DAY_LABELS: Record<DayOfWeekValue, { short: string; long: string }> = {
    1: { short: "Mon", long: "Monday" },
    2: { short: "Tue", long: "Tuesday" },
    3: { short: "Wed", long: "Wednesday" },
    4: { short: "Thu", long: "Thursday" },
    5: { short: "Fri", long: "Friday" },
    6: { short: "Sat", long: "Saturday" },
    7: { short: "Sun", long: "Sunday" },
};

const TIME_SLOTS = Array.from({ length: 33 }, (_, i) => {
    const m = (6 * 60 + i * 30);
    return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
});

function displayTime(t: string): string {
    const [hh, mm] = t.split(":").map(Number);
    const p = hh < 12 ? "AM" : "PM";
    const h = hh === 0 ? 12 : hh > 12 ? hh - 12 : hh;
    return mm === 0 ? `${h} ${p}` : `${h}:${String(mm).padStart(2, "0")} ${p}`;
}

export interface BusinessHoursCardProps {
    hoursList: BusinessHours[];
    onUpdateSlot: (id: number, startTime: string, endTime: string) => void;
    onToggleDay: (dayOfWeek: DayOfWeekValue) => void;
    onAddSlot: (dayOfWeek: DayOfWeekValue) => void;
    onRemoveSlot: (id: number) => void;
}

export function BusinessHoursCard({ hoursList, onUpdateSlot, onToggleDay, onAddSlot, onRemoveSlot }: BusinessHoursCardProps) {
    // slot.id! used throughout — id is always present from API, BusinessHours.id is typed optional speculatively
    const hoursByDay = hoursList.reduce((acc, h) => {
        (acc[h.day_of_week] ??= []).push(h);
        return acc;
    }, {} as Record<DayOfWeekValue, BusinessHours[]>);

    return (
        <SettingsCard title="Business Hours">
            <div className="flex flex-col gap-2">
                {([1, 2, 3, 4, 5, 6, 7] as DayOfWeekValue[]).map((day) => {
                    const info = DAY_LABELS[day];
                    const slots = hoursByDay[day] || [];
                    const isClosed = slots.length === 0;

                    return (
                        <div key={day} className={`flex flex-col p-3 rounded-xl border transition-colors ${isClosed ? "bg-white border-blue-100" : "bg-white border-blue-200"}`}>
                            <div className="flex items-center justify-between">
                                <span className={`text-base font-semibold ${isClosed ? "text-blue-400" : "text-blue-950"}`}>
                                    {info.long}
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
                                    {slots.map((slot) => (
                                        <div key={slot.id} className="flex items-center gap-2">
                                            <select
                                                value={slot.start_time}
                                                onChange={(e) => onUpdateSlot(slot.id!, e.target.value, slot.end_time)}
                                                className="flex-1 min-w-0 px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 cursor-pointer focus:outline-none focus:border-blue-500"
                                            >
                                                {TIME_SLOTS.map((t) => (
                                                    <option key={t} value={t}>{displayTime(t)}</option>
                                                ))}
                                            </select>
                                            <span className="text-blue-300 text-xs shrink-0">to</span>
                                            <select
                                                value={slot.end_time}
                                                onChange={(e) => onUpdateSlot(slot.id!, slot.start_time, e.target.value)}
                                                className="flex-1 min-w-0 px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 cursor-pointer focus:outline-none focus:border-blue-500"
                                            >
                                                {TIME_SLOTS.map((t) => (
                                                    <option key={t} value={t}>{displayTime(t)}</option>
                                                ))}
                                            </select>
                                            <Button
                                                infoMessage="Remove time period"
                                                onClick={() => onRemoveSlot(slot.id!)}
                                                variant="minimal"    
                                            >
                                                <CloseIcon/>
                                            </Button>
                                        </div>
                                    ))}
                                    <Button
                                        variant="solid"
                                        onClick={() => onAddSlot(day)}
                                        infoMessage="Added a new slot"
                                    >
                                        + Add time period
                                    </Button>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </SettingsCard>
    );
}
