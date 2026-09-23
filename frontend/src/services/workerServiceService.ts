import { apiClient } from "./ApiClient";
import type { WorkerService } from "../types/worker";

export async function createWorkerAssignment(service_id: number, worker_id: number): Promise<WorkerService> {
    const response = await apiClient.post(`/worker-service?business_id=1&service_id=${service_id}&worker_id=${worker_id}`);
    return response.data;
}

export async function getWorkerAssignments(): Promise<Record<number, number[]>> {
    const response = await apiClient.get(`/worker-service?business_id=1`);
    return response.data;
}

export async function deleteWorkerAssignment(service_id: number, worker_id: number): Promise<{ service_id: number; worker_id: number }> {
    const response = await apiClient.delete(`/worker-service?business_id=1&service_id=${service_id}&worker_id=${worker_id}`);
    return response.data;
}
