interface SectionHeaderProps {
    title: String;
    subtitle: String;
}

export function SectionHeader({ title, subtitle } : SectionHeaderProps) {
    return(
        <div className="flex flex-col items-center max-w-6xl mx-auto mb-8">
            <h1 className="text-2xl font-bold text-blue-950">{title}</h1>
            <p className="text-center text-blue-800 mt-1">{subtitle}</p>
        </div>
    )
}