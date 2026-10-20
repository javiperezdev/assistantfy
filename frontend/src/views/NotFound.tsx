import { Link } from 'react-router-dom';

export function NotFound() {
    return (
        <div className="bg-blue-50 min-h-screen flex flex-col items-center justify-center text-center px-6 py-16 gap-4 md:gap-6">
            <span className="text-2xl font-semibold tracking-wide text-blue-600">Assistanfy</span>
            <h1 className="text-7xl md:text-9xl font-bold text-blue-950 leading-none">404</h1>
            <h2 className="text-2xl font-bold text-blue-950">Page not found</h2>
            <p className="text-sm font-normal text-blue-800 max-w-md">
                The page you are looking for doesn't exist or has been moved.
            </p>
            <Link
                to="/"
                className="mt-2 h-10 px-4 border border-blue-600 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 transition-colors inline-flex items-center justify-center"
            >
                Back to home
            </Link>
        </div>
    );
}
