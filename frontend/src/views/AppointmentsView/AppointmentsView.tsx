import TopNavigation from "../../components/TopNavigation";
import { AppointmentsContainer } from "./AppointmentsContainer";

export function AppointmentsView() {
    return (
        <div className="bg-white min-h-screen p-6 md:p-10">
            <TopNavigation />
            <div className="bg-white min-h-screen">
                <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col gap-8">
                    <div className="flex flex-col items-center">
                            <h1 className="text-2xl font-bold text-blue-950">Appointments</h1>
                            <p className="text-blue-800 mt-1">Manage your appointments</p>
                    </div>

                    <AppointmentsContainer />
                </div>
            </div>
        </div>
    );
}
