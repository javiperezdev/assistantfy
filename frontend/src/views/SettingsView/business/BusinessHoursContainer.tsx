import { useState } from 'react';
import { useBusinessHours, useCreateBusinessHours, useUpdateBusinessHour, useDeleteBusinessHour } from '../../../hooks/useBusiness';
import type { DayOfWeekValue } from '../../../types/business';
import { BusinessHoursCard } from './BusinessHoursCard';
import { Toast } from '../../../components/Toast';
import { LoadingSpinner } from '../../../components/LoadingSpinner';
import { ErrorMessage } from '../../../components/ErrorMessage';

function overlaps(a: string, b: string, c: string, d: string): boolean {
    return a < d && c < b;
}

export function BusinessHoursContainer() {
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
    const { data: hours, isPending, isError, refetch } = useBusinessHours();
    const { mutate: createBusinessHours } = useCreateBusinessHours();
    const { mutate: updateBusinessHour } = useUpdateBusinessHour();
    const { mutate: deleteBusinessHour } = useDeleteBusinessHour();

    const onError = () => setToast({ message: "Something went wrong", type: "error" });
    const onSuccess = (msg: string) => setToast({ message: msg, type: "success" });

    const handleUpdateSlot = (id: number, startTime: string, endTime: string) => {
        const slot = hours?.find(h => h.id === id);
        if (!slot) return;
        if (startTime >= endTime) {
            setToast({ message: "Start time must be before end time", type: "error" });
            return;
        }
        const siblings = hours?.filter(h => h.day_of_week === slot.day_of_week && h.id !== id) ?? [];
        if (siblings.some(s => overlaps(startTime, endTime, s.start_time, s.end_time))) {
            setToast({ message: "Time slots cannot overlap", type: "error" });
            return;
        }
        updateBusinessHour({ ...slot, start_time: startTime, end_time: endTime }, {
            onSuccess: () => onSuccess("Business hours updated"),
            onError,
        });
    };

    const handleToggleDay = (dayOfWeek: DayOfWeekValue) => {
        const daySlots = hours?.filter(h => h.day_of_week === dayOfWeek) ?? [];
        if (daySlots.length > 0) {
            daySlots.forEach(s => deleteBusinessHour(s.id!, {
                onSuccess: () => onSuccess("Business hours updated"),
                onError,
            }));
        } else {
            // business_id=1 hardcoded
            createBusinessHours({ business_id: 1, day_of_week: dayOfWeek, start_time: "09:00", end_time: "17:00" }, {
                onSuccess: () => onSuccess("Business hours updated"),
                onError,
            });
        }
    };

    const handleAddSlot = (dayOfWeek: DayOfWeekValue) => {
        const daySlots = hours?.filter(h => h.day_of_week === dayOfWeek) ?? [];
        const last = daySlots[daySlots.length - 1];
        const start = last ? last.end_time : "09:00";
        const [h, m] = start.split(":").map(Number);
        const end = `${String(Math.min(h + 1, 23)).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
        createBusinessHours({ business_id: 1, day_of_week: dayOfWeek, start_time: start, end_time: end }, {
            onSuccess: () => onSuccess("Business hours updated"),
            onError,
        });
    };

    const handleRemoveSlot = (id: number) => {
        deleteBusinessHour(id, {
            onSuccess: () => onSuccess("Business hours updated"),
            onError,
        });
    };

    if (isPending) return <LoadingSpinner message="Loading business hours..." size="md" />;
    if (isError) return <ErrorMessage fullPage message="We couldn't load business hours. Please try again." onRetry={() => refetch()} />;

    return (
        <>
            <BusinessHoursCard hoursList={hours} onUpdateSlot={handleUpdateSlot} onToggleDay={handleToggleDay} onAddSlot={handleAddSlot} onRemoveSlot={handleRemoveSlot} />
            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}
        </>
    );
}
