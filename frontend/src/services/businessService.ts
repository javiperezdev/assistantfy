import { apiClient } from "./ApiClient";
import type { BusinessHours } from "../types/business";

export async function getBusinessHours(): Promise<BusinessHours[]> {
    const response = await apiClient.get("business-hours?business_id=1");
    return response.data.map((h: BusinessHours) => ({
        ...h,
        start_time: h.start_time.substring(0, 5),
        end_time: h.end_time.substring(0, 5),
    }));
}

export async function createBusinessHours(day_of_week: number, start_time: string, end_time: string): Promise<BusinessHours> {
    const response = await apiClient.post(`/business-hours?business_id=1&day_of_week=${day_of_week}&start_time=${start_time}&end_time=${end_time}`);
    return response.data;
}

export async function updateBusinessHours(id: number, day_of_week: number, start_time: string, end_time: string): Promise<BusinessHours> {
    const response = await apiClient.put(`/business-hours?id=${id}&business_id=1&day_of_week=${day_of_week}&start_time=${start_time}&end_time=${end_time}`);
    return response.data;
}

export async function deleteBusinessHours(id: number): Promise<void> {
    await apiClient.delete(`/business-hours?business_id=1&id=${id}`);
}
