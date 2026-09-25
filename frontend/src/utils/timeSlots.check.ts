// Self-check if errors occur in timeSlots.ts. Run with: npx tsx src/utils/timeSlots.check.ts
import { TIME_SLOTS, nextSlotEnd } from "./timeSlots";

function expect(actual: string | null, wanted: string | null, label: string) {
    if (actual !== wanted) throw new Error(`${label}: expected "${wanted}", got "${actual}"`);
}

expect(TIME_SLOTS[0], "06:00", "first slot");
expect(TIME_SLOTS[TIME_SLOTS.length - 1], "22:00", "last slot");
expect(nextSlotEnd("09:00"), "10:00", "plain chaining");
expect(nextSlotEnd("21:30"), "22:00", "capped to last slot");
expect(nextSlotEnd("17:00:00"), "18:00", "business API returns seconds");
expect(nextSlotEnd("22:00"), null, "no room at the end of the day");
expect(nextSlotEnd("22:00:00"), null, "no room (with seconds)");

console.log("timeSlots checks passed");
