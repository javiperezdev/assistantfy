import { WorkerContainer } from "./workers/WorkerContainer";
import { ServicesContainer } from "./services/ServicesContainer";
import { BusinessHoursContainer } from "./business/BusinessHoursContainer";
import { SectionHeader } from "../../components/SectionHeader";
import { TopNavigation }  from "../../components/TopNavigation";

export function SettingView() {
    
    return (
        <div className="bg-white min-h-screen p-6 md:p-10">
            <TopNavigation />
            <SectionHeader title="Configurations" subtitle="Manage your team, services and business hours."/>
            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">       
                <WorkerContainer />
                <ServicesContainer />
                <BusinessHoursContainer />
            </div>
        </div>
    );
}