import { apiClient } from "./ApiClient";
import type { WorkerHours } from "../types/worker";

// business_id is hardcoded to 1 for testing purposes. 

export async function getWorkerHours(workerId: number): Promise<WorkerHours[]> {
    const response = await apiClient.get(`/worker-hours?worker_id=${workerId}&business_id=1`);
    return response.data.map((h: WorkerHours) => ({ // format change to fit the frontend's format.
            ...h,
            start_time: h.start_time.slice(0, 5),
            end_time: h.end_time.slice(0, 5),
        }));
}

export async function deleteWorkerHours(workerHoursId: number, workerId: number): Promise<void> {
    await apiClient.delete(`/worker-hours?id=${workerHoursId}&worker_id=${workerId}&business_id=1`);
}


