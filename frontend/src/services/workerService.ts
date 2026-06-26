import { apiClient } from "./ApiClient";
import type { Worker } from "../types/worker";

export async function getWorkers(): Promise<Worker[]> {
    try {
        // Currently querying business=1 for local development
        const response = await apiClient.get("/workers?business_id=1");
        return response.data;
    }
    catch (error) {
        console.error("Error fetching data:", error);
    } 
}

