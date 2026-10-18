import { apiClient } from "./ApiClient";
import type { Appointment, AppointmentState } from "../types/appointment";

export async function getAppointments(date: string): Promise<Appointment[]> {
    const response = await apiClient.get(`/appointments?business_id=1&date=${date}`);
    return response.data;
}

export async function updateAppointmentState(appointment_id: number, new_state: AppointmentState) {
    const response = await apiClient.patch(`/appointment/state?business_id=1&appointment_id=${appointment_id}&new_state=${new_state}`);
    return response.data;
}

export async function createAppointment(
    phone_number: string,
    service_id: number,
    start_time: string,
    name?: string,
    worker_id?: number
) {
    // If name or worker_id are not provided, they won't appear in the query string.
    const response = await apiClient.post(
        `/appointments?business_id=1&phone_number=${phone_number}&service_id=${service_id}&start_time=${start_time}` +
        `${name ? `&name=${name}` : ""}${worker_id !== undefined ? `&worker_id=${worker_id}` : ""}`
    );
    return response.data;
}
