import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-emerald-500">FinWise</h1>
                    <div className="flex items-center gap-4">
                        <span className="text-gray-400">Olá, {user?.name}</span>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                        >
                            Sair
                        </button>
                    </div>
                </div>

                <div className="bg-gray-800 rounded-lg p-8 text-center">
                    <h2 className="text-2xl font-semibold mb-4">🎉 Dashboard</h2>
                    <p className="text-gray-400">Dashboard em construção...</p>
                </div>
            </div>
        </div>
    );
}