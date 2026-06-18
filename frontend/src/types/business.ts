export interface Business {
    id?: number;
    phone_number: string;
    name: string;
    timezone: string;
}

export type DayOfWeekValue = 1 | 2 | 3 | 4 | 5 | 6 | 7

export interface BusinessHours {
    id?: number;
    business_id: number;
    day_of_week: DayOfWeekValue;
    start_time: string;
    end_time: string;
}