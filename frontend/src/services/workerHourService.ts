import { apiClient } from "./ApiClient";
import type { WorkerHours } from "../types/worker";

export async function getWorkerHours(workerId: number): Promise<WorkerHours[]> {
    const response = await apiClient.get(`/worker-hours?worker_id=${workerId}`);
    return response.data.map((h: WorkerHours) => ({ // format change to fit the frontend's format.
            ...h,
            start_time: h.start_time.slice(0, 5),
            end_time: h.end_time.slice(0, 5),
        }));
}

export async function deleteWorkerHours(workerHoursId: number, workerId: number): Promise<void> {
    await apiClient.delete(`/worker-hours?id=${workerHoursId}&worker_id=${workerId}`);
}

export async function createWorkerHour(workerId: number, dayOfWeek: number, start_time: string, end_time: string): Promise<void> {
    await apiClient.post(`/worker-hours?worker_id=${workerId}&day_of_week=${dayOfWeek}&start_time=${start_time}&end_time=${end_time}`);
}

export async function patchWorkerHoursDay(workerId: number, dayOfWeek: number, isActive: boolean): Promise<void> {
    await apiClient.patch(`/worker-hours/day?worker_id=${workerId}&day_of_week=${dayOfWeek}&is_active=${isActive}`);
}

export async function putWorkerHours(workerHoursId: number, workerId: number, dayOfWeek: number, start_time: string, end_time: string): Promise<void> {
    await apiClient.put(`/worker-hours?id=${workerHoursId}&worker_id=${workerId}&day_of_week=${dayOfWeek}&start_time=${start_time}&end_time=${end_time}`);
}
