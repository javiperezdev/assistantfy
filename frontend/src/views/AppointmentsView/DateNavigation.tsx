interface DateNavigationProps {
    date: Date;
    onPrevDay: () => void;
    onNextDay: () => void;
}

const arrowStyles = "w-8 h-8 flex items-center justify-center border border-blue-200 rounded-lg text-blue-950 text-lg leading-none hover:bg-blue-50 transition-colors cursor-pointer";

export function DateNavigation({ date, onPrevDay, onNextDay }: DateNavigationProps) {
    const isToday = date.toDateString() === new Date().toDateString();
    const label = isToday
        ? `Today, ${date.toLocaleDateString("en-US", { month: "long", day: "numeric" })}`
        : date.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

    return (
        <div className="flex items-center justify-center gap-3">
            <button className={arrowStyles} onClick={onPrevDay} aria-label="Previous day">‹</button>
            <span className="text-blue-950 font-semibold">{label}</span>
            <button className={arrowStyles} onClick={onNextDay} aria-label="Next day">›</button>
        </div>
    );
}
