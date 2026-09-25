export const TIME_SLOTS = Array.from({ length: 33 }, (_, i) => {
    const m = (6 * 60 + i * 30);
    return `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
});

const LAST_SLOT = TIME_SLOTS[TIME_SLOTS.length - 1];

/** Next hour after `start`, capped at the last selectable slot. Null when there is no room left. */
export function nextSlotEnd(start: string): string | null {
    const [h, m] = start.split(":").map(Number);
    const end = `${String(h + 1).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
    const capped = end > LAST_SLOT ? LAST_SLOT : end;
    return capped > start ? capped : null;
}
