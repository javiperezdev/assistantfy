import { apiClient } from "./ApiClient";
import type { Service } from "../types/service";

export async function getServices(): Promise<Service[]> {
    const response = await apiClient.get("services");
    return response.data;
}

export async function createService(name: string, price: number, duration_minutes: number): Promise<Service> {
    const response = await apiClient.post(`/service?service_name=${name}&price=${price}&duration_minutes=${duration_minutes}`);
    return response.data;
}

export async function deleteService(id: number): Promise<{ name: string }> {
    const response = await apiClient.delete(`/service?id=${id}`);
    return response.data;
}
