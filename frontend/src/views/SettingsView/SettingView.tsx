import { WorkerContainer } from "./WorkerContainer";

export function SettingView() {
    
    return (
        <div className="bg-slate-50 min-h-screen p-6 md:p-10">
            <div className="max-w-6xl mx-auto mb-8">
                <h1 className="text-3xl font-bold text-slate-900">Configurations</h1>
                <p className="text-slate-500 mt-1">Manage your team members and operational catalog.</p>
            </div>

            <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">       
                <WorkerContainer />
                <div className="bg-white rounded-xl border border-slate-200 border-dashed p-6 text-center text-slate-400">
                    Services Panel (Coming Soon)
                </div>
                <div className="bg-white rounded-xl border border-slate-200 border-dashed p-6 text-center text-slate-400">
                    Business Hours (Coming Soon)
                </div>
            </div>
        </div>
    );
}