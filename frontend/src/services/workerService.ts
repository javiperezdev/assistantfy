import { apiClient } from "./ApiClient";
import type { Worker } from "../types/worker";

export async function getWorkers(): Promise<Worker[]> {
    const response = await apiClient.get("/workers");
    return response.data;
}

export async function addWorker(name: string): Promise<Worker> {
    const response = await apiClient.post(`/worker?worker_name=${name}`);
    return response.data;
}

export async function deleteWorker(id: number): Promise<Worker> {
    const response = await apiClient.delete(`/worker?worker_id=${id}`);
    return response.data;
}
