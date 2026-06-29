import { useState } from 'react';
import type { BusinessHours, DayOfWeekValue } from '../../../types/business';
import { BusinessHoursCard } from './BusinessHoursCard';

const MOCK_HOURS: BusinessHours[] = [
    { id: 1, business_id: 1, day_of_week: 1, start_time: "09:00", end_time: "18:00" },
    { id: 2, business_id: 1, day_of_week: 2, start_time: "09:00", end_time: "18:00" },
    { id: 3, business_id: 1, day_of_week: 3, start_time: "09:00", end_time: "18:00" },
    { id: 4, business_id: 1, day_of_week: 4, start_time: "09:00", end_time: "18:00" },
    { id: 5, business_id: 1, day_of_week: 5, start_time: "09:00", end_time: "17:00" },
    { id: 6, business_id: 1, day_of_week: 6, start_time: "10:00", end_time: "15:00" },
];
let nextId = 7;

export function BusinessHoursContainer() {
    const [hours, setHours] = useState<BusinessHours[]>(MOCK_HOURS);

    const handleUpdateHours = (dayOfWeek: DayOfWeekValue, startTime: string, endTime: string) => {
        const existing = hours.find(h => h.day_of_week === dayOfWeek);
        if (existing) {
            setHours(hours.map(h => h.id === existing.id ? { ...h, start_time: startTime, end_time: endTime } : h));
        } else {
            const newHours: BusinessHours = {
                id: nextId++,
                business_id: 1,
                day_of_week: dayOfWeek,
                start_time: startTime,
                end_time: endTime,
            };
            setHours([...hours, newHours]);
        }
    };

    const handleToggleDay = (dayOfWeek: DayOfWeekValue) => {
        const existing = hours.find(h => h.day_of_week === dayOfWeek);
        if (existing) {
            setHours(hours.filter(h => h.day_of_week !== dayOfWeek));
        } else {
            const newHours: BusinessHours = {
                id: nextId++,
                business_id: 1,
                day_of_week: dayOfWeek,
                start_time: "09:00",
                end_time: "17:00",
            };
            setHours([...hours, newHours]);
        }
    };

    return (
        <BusinessHoursCard
            hoursList={hours}
            onUpdateHours={handleUpdateHours}
            onToggleDay={handleToggleDay}
        />
    );
}