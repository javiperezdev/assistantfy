import { apiClient } from "./ApiClient";
import type { Appointment } from "../types/appointment";

export async function getAppointments(date: string): Promise<Appointment[]> {
    const response = await apiClient.get(`/appointments?business_id=1&date=${date}`);
    return response.data;
}
