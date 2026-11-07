import { useQuery } from "@tanstack/react-query";
import { getMe } from "../services/authService";

export function useAuth() {
    return useQuery({
        queryKey: ["auth", "me"],
        queryFn: getMe,
        // A 401 here means "no session"; let the caller handle it, don't retry.
        retry: false,
        // The session is verified once per app load; dashboard endpoints still
        // enforce it on every call, so re-checking /me on each route change
        // would only add a redundant round-trip.
        staleTime: Infinity,
    });
}
