import { useCallback, useState } from "react";
import { useLocation } from "react-router-dom";
import { TopNavigation } from "../../components/TopNavigation";
import { AppointmentsContainer } from "./AppointmentsContainer";
import { SectionHeader } from "../../components/SectionHeader";
import { Toast } from "../../components/Toast";


interface WelcomeState {
    welcomeEmail?: string;
}

export function AppointmentsView() {
    const location = useLocation();
    const [welcomeEmail, setWelcomeEmail] = useState<string | null>(
        (location.state as WelcomeState | null)?.welcomeEmail ?? null
    );
    const dismissWelcome = useCallback(() => setWelcomeEmail(null), []);

    return (
        <div className="bg-white min-h-screen p-6 md:p-10">
            {welcomeEmail && (
                <Toast message={`Welcome back, ${welcomeEmail}`} onClose={dismissWelcome} />
            )}
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
