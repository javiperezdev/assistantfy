import { Link } from "react-router-dom";
import { Button } from "./Button";

export function TopNavigation() {
    return (
        <div className="flex flex-col items-center gap-4 px-6 py-4 max-w-7xl mx-auto justify-between md:flex-row">
            <h1 className="text-3xl font-bold text-blue-950">Assistantfy</h1>
            <div className="flex items-center">
                <div>
                    <Link to="/">
                        <Button infoMessage="Opened Appointments view" variant="minimal">Appointments</Button>
                    </Link>
                </div>
                <div>
                    <Link to="/settings">
                        <Button infoMessage="Opened Settings menu" variant="minimal">Settings</Button>
                    </Link>
                </div>
            </div>
        </div>
    )
}