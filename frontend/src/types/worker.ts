export interface Worker {
    id?: number;
    business_id: number;
    name: string;
}

export interface WorkerHours {
    id?: number;
    worker_id: number;
    day_of_week: number;
    start_time: string;
    end_time: string;
}

export interface WorkerService {
    service_id: number;
    worker_id: number;
}