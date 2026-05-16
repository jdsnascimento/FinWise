import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Register() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Senhas não conferem');
            return;
        }

        setLoading(true);

        try {
            await register({
                name: formData.name,
                email: formData.email,
                phone: formData.phone || null,
                password: formData.password
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao cadastrar');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-emerald-500">FinWise</h1>
                    <p className="mt-2 text-gray-400">Crie sua conta gratuita</p>
                </div>

                <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-8 space-y-6">
                    <h2 className="text-2xl font-semibold text-white text-center">Cadastro</h2>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Nome</label>
                        <input
                            type="text"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="Seu nome completo"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="seu@email.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">WhatsApp (opcional)</label>
                        <input
                            type="text"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="5511999999999"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Senha</label>
                        <input
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="Mínimo 6 caracteres"
                            required
                            minLength={6}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Confirmar Senha</label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                            placeholder="Repita a senha"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2 px-4 bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-800 text-white rounded-lg font-medium transition-colors"
                    >
                        {loading ? 'Cadastrando...' : 'Criar Conta'}
                    </button>

                    <p className="text-center text-gray-400 text-sm">
                        Já tem conta?{' '}
                        <Link to="/login" className="text-emerald-500 hover:text-emerald-400">
                            Faça login
                        </Link>
                    </p>
                </form>
            </div>
        </div>
    );
}