import { apiClient } from "./ApiClient";
import type { Worker } from "../types/worker";

// Currently querying business=1 for local development

export async function getWorkers(): Promise<Worker[]> {
    const response = await apiClient.get("/workers?business_id=1");
    return response.data;
}

export async function addWorker(name: string): Promise<Worker> {
    try {
        const response = await apiClient.post(`/worker?business_id=1&worker_name=${name}`);
        return response.data;
    }
    catch {
        return undefined;
    }
}

export async function deleteWorker(id: number): Promise<Worker> {
    const response = await apiClient.delete(`/worker?business_id=1&worker_id=${id}`);
    return response.data;
    } 