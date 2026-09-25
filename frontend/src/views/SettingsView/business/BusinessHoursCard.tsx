import type { BusinessHours, DayOfWeekValue } from '../../../types/business';
import { SettingsCard } from '../../../components/SettingsCard';
import { HoursDayList } from '../../../components/HoursDayList';

export interface BusinessHoursCardProps {
    hoursList: BusinessHours[];
    onUpdateSlot: (id: number, startTime: string, endTime: string) => void;
    onToggleDay: (dayOfWeek: DayOfWeekValue) => void;
    onAddSlot: (dayOfWeek: DayOfWeekValue) => void;
    onRemoveSlot: (id: number) => void;
}

export function BusinessHoursCard({ hoursList, onUpdateSlot, onToggleDay, onAddSlot, onRemoveSlot }: BusinessHoursCardProps) {
    return (
        <SettingsCard title="Business Hours">
            <HoursDayList
                slots={hoursList}
                onToggleDay={onToggleDay}
                // id! always present from API; BusinessHours.id is typed optional speculatively
                onSlotChange={(slot, startTime, endTime) => onUpdateSlot(slot.id!, startTime, endTime)}
                onAddSlot={onAddSlot}
                onRemoveSlot={(slot) => onRemoveSlot(slot.id!)}
            />
        </SettingsCard>
    );
}
