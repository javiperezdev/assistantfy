import { TopNavigation } from "../../components/TopNavigation";
import { AppointmentsContainer } from "./AppointmentsContainer";
import { SectionHeader } from "../../components/SectionHeader";


export function AppointmentsView() {
    return (
        <div className="bg-white min-h-screen p-6 md:p-10">
            <TopNavigation />
            <SectionHeader title="Appointments" subtitle="Manage your appointments"/>
            <div className="bg-white min-h-screen">
                <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col gap-8">
                    <AppointmentsContainer />
                </div>
            </div>
        </div>
    );
}
