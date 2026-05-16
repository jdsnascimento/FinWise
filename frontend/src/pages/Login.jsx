import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao fazer login');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-emerald-500">FinWise</h1>
                    <p className="mt-2 text-gray-400">Controle financeiro inteligente</p>
                </div>

                <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-8 space-y-6">
                    <h2 className="text-2xl font-semibold text-white text-center">Login</h2>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="seu@email.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Senha</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="••••••"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2 px-4 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-800 text-white rounded-lg font-medium transition-colors"
                    >
                        {loading ? 'Entrando...' : 'Entrar'}
                    </button>

                    <p className="text-center text-gray-400 text-sm">
                        Não tem conta?{' '}
                        <Link to="/register" className="text-emerald-500 hover:text-emerald-400">
                            Cadastre-se
                        </Link>
                    </p>
                </form>
            </div>
        </div>
    );
}