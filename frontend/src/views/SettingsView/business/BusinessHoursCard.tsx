import { useState } from 'react';
import type { BusinessHours, DayOfWeekValue } from '../../../types/business';
import { Button } from '../../../components/Button';
import { SettingsCard } from '../../../components/SettingsCard';

const DAY_LABELS: Record<DayOfWeekValue, { short: string; long: string }> = {
    1: { short: "Mon", long: "Monday" },
    2: { short: "Tue", long: "Tuesday" },
    3: { short: "Wed", long: "Wednesday" },
    4: { short: "Thu", long: "Thursday" },
    5: { short: "Fri", long: "Friday" },
    6: { short: "Sat", long: "Saturday" },
    7: { short: "Sun", long: "Sunday" },
};

function EditIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125" />
        </svg>
    );
}

function CheckIcon() {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
    );
}

export interface BusinessHoursCardProps {
    hoursList: BusinessHours[];
    onUpdateHours: (dayOfWeek: DayOfWeekValue, startTime: string, endTime: string) => void;
    onToggleDay: (dayOfWeek: DayOfWeekValue) => void;
}

export function BusinessHoursCard({ hoursList, onUpdateHours, onToggleDay }: BusinessHoursCardProps) {
    const [editingDay, setEditingDay] = useState<DayOfWeekValue | null>(null);
    const [editStart, setEditStart] = useState("");
    const [editEnd, setEditEnd] = useState("");

    const hoursByDay = Object.fromEntries(
        hoursList.map(h => [h.day_of_week, h])
    ) as Record<DayOfWeekValue, BusinessHours | undefined>;

    const startEditing = (day: DayOfWeekValue) => {
        const existing = hoursByDay[day];
        setEditStart(existing?.start_time || "09:00");
        setEditEnd(existing?.end_time || "17:00");
        setEditingDay(day);
    };

    const saveEditing = () => {
        if (editingDay !== null) {
            onUpdateHours(editingDay, editStart, editEnd);
            setEditingDay(null);
        }
    };

    const cancelEditing = () => {
        setEditingDay(null);
    };

    return (
        <SettingsCard title="Business Hours">
            <div className="space-y-1">
                {([1, 2, 3, 4, 5, 6, 7] as DayOfWeekValue[]).map((day) => {
                    const info = DAY_LABELS[day];
                    const hours = hoursByDay[day];
                    const isEditing = editingDay === day;
                    const isClosed = !hours;

                    return (
                        <div
                            key={day}
                            className={`group flex items-center justify-between p-3 rounded-xl transition-colors ${
                                isEditing ? "bg-blue-50 border border-blue-200" : "hover:bg-blue-50/60 border border-transparent"
                            }`}
                        >
                            <div className="flex items-center gap-3 min-w-0 flex-1">
                                <div className="flex flex-col min-w-0">
                                    <span className={`text-base font-semibold ${isClosed ? "text-blue-400" : "text-blue-950"}`}>
                                        {info.long}
                                    </span>
                                    {isEditing ? (
                                        <div className="flex items-center gap-2 mt-1">
                                            <input
                                                type="time"
                                                value={editStart}
                                                onChange={(e) => setEditStart(e.target.value)}
                                                className="px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 focus:outline-none focus:border-blue-500"
                                            />
                                            <span className="text-blue-400 text-xs">to</span>
                                            <input
                                                type="time"
                                                value={editEnd}
                                                onChange={(e) => setEditEnd(e.target.value)}
                                                className="px-2 py-1 text-sm border border-blue-200 rounded-lg bg-white text-blue-950 focus:outline-none focus:border-blue-500"
                                            />
                                            <div className="flex items-center gap-1">
                                                <Button onClick={saveEditing} infoMessage="Save hours" variant="minimal">
                                                    <CheckIcon />
                                                </Button>
                                                <Button onClick={cancelEditing} infoMessage="Cancel" variant="minimal">
                                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                                    </svg>
                                                </Button>
                                            </div>
                                        </div>
                                    ) : (
                                        <span className="text-sm font-medium text-blue-600">
                                            {isClosed ? "Closed" : `${hours.start_time} — ${hours.end_time}`}
                                        </span>
                                    )}
                                </div>
                            </div>

                            {!isEditing && (
                                <div className="flex items-center gap-1 shrink-0">
                                    <Button onClick={() => startEditing(day)} infoMessage={`Edit ${info.long}`} variant="minimal">
                                        <EditIcon />
                                    </Button>
                                    <Button onClick={() => onToggleDay(day)} infoMessage={isClosed ? `Open ${info.long}` : `Close ${info.long}`} variant="minimal">
                                        {isClosed ? (
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-blue-500 hover:text-green-500">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                                            </svg>
                                        ) : (
                                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                                            </svg>
                                        )}
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