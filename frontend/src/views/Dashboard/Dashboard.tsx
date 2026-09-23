import { Button } from "../../components/Button"
import { Link } from "react-router-dom"

export function Dashboard() {
    return (
        <div>
            <h1>Business Owner</h1>
            <Link to="/settings">
                <Button infoMessage="Opened Settings menu" variant="minimal">Settings</Button>
            </Link>
        </div>
    )
}