import { WorkerContainer } from "./workers/WorkerContainer";
import { SettingsCard } from "../../components/SettingsCard";

export function SettingView() {
    
    return (
        <div className="bg-white min-h-screen p-6 md:p-10">
            <div className="max-w-6xl mx-auto mb-8">
                <h1 className="text-3xl font-bold text-blue-950">Configurations</h1>
                <p className="text-blue-800 mt-1">Manage your team, services and business hours.</p>
            </div>

            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">       
                <WorkerContainer />
                <SettingsCard isPlaceholder>
                    Services Panel (Coming Soon)
                </SettingsCard>
                <SettingsCard isPlaceholder>
                    Business Hours (Coming Soon)
                </SettingsCard>
            </div>
        </div>
    );
}