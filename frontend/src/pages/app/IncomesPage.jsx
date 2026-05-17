/* eslint-disable react-hooks/exhaustive-deps, react-hooks/set-state-in-effect */
import { useState, useEffect } from 'react';
import {
    Plus,
    MagnifyingGlass,
    CheckCircle,
    Trash,
    Calendar,
    TrendUp,
    Money
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import { incomeService } from '../../services/income.service';
import { categoryService } from '../../services/category.service';

export default function IncomesPage() {
    const [incomes, setIncomes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [categories, setCategories] = useState([]);
    const [filters, setFilters] = useState({
        status: '',
        search: ''
    });

    const [formData, setFormData] = useState({
        description: '',
        amount: '',
        expected_date: new Date().toISOString().split('T')[0],
        category_id: '',
        recurring: false,
        recurrence_type: null,
        notes: ''
    });
    const [error, setError] = useState('');
    const [summary, setSummary] = useState(null);

    const loadIncomes = async () => {
        try {
            setLoading(true);
            const params = {};
            if (filters.status) params.status = filters.status;
            if (filters.search) params.search = filters.search;

            const data = await incomeService.listAll(params);
            setIncomes(data);
        } catch (err) {
            console.error('Erro ao carregar receitas:', err);
        } finally {
            setLoading(false);
        }
    };

    const loadCategories = async () => {
        try {
            const data = await categoryService.listAll('income');
            setCategories(data);
        } catch (err) {
            console.error('Erro ao carregar categorias:', err);
        }
    };

    const loadSummary = async () => {
        try {
            const data = await incomeService.getSummary();
            setSummary(data);
        } catch (err) {
            console.error('Erro ao carregar resumo:', err);
        }
    };

    useEffect(() => {
        loadIncomes();
        loadCategories();
        loadSummary();
    }, [filters]);

    const openCreateModal = () => {
        setFormData({
            description: '',
            amount: '',
            expected_date: new Date().toISOString().split('T')[0],
            category_id: categories[0]?.id || '',
            recurring: false,
            recurrence_type: null,
            notes: ''
        });
        setError('');
        setModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const data = {
                ...formData,
                amount: parseFloat(formData.amount),
                category_id: parseInt(formData.category_id),
                recurring: formData.recurring,
                recurrence_type: formData.recurring ? formData.recurrence_type : null
            };

            await incomeService.create(data);
            setModalOpen(false);
            loadIncomes();
            loadSummary();
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao salvar receita');
        }
    };

    const handleReceive = async (id) => {
        try {
            await incomeService.receive(id);
            loadIncomes();
            loadSummary();
        } catch {
            alert('Erro ao marcar como recebida');
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('Excluir esta receita?')) return;
        try {
            await incomeService.delete(id);
            loadIncomes();
            loadSummary();
        } catch {
            alert('Erro ao excluir receita');
        }
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    };

    const formatDate = (dateStr) => {
        return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            pending: { variant: 'warning', label: 'Pendente' },
            received: { variant: 'success', label: 'Recebido' },
            late: { variant: 'danger', label: 'Atrasado' },
            cancelled: { variant: 'default', label: 'Cancelado' }
        };
        const s = statusMap[status] || statusMap.pending;
        return <Badge variant={s.variant}>{s.label}</Badge>;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Contas a Receber</h1>
                    <p className="text-gray-400 mt-1">Gerencie suas receitas e entradas</p>
                </div>
                <Button icon={Plus} onClick={openCreateModal}>
                    Nova Receita
                </Button>
            </div>

            {/* Cards de Resumo */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <TrendUp size={24} className="text-blue-500" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Total Previsto</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(summary.total_expected)}</p>
                            </div>
                        </div>
                    </Card>
                    <Card>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-500/10 rounded-lg">
                                <CheckCircle size={24} className="text-emerald-500" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Total Recebido</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(summary.total_received)}</p>
                            </div>
                        </div>
                    </Card>
                    <Card>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-yellow-500/10 rounded-lg">
                                <Money size={24} className="text-yellow-500" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Pendentes ({summary.pending_count})</p>
                                <p className="text-xl font-bold text-white">{formatCurrency(summary.total_pending)}</p>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* Filtros */}
            <Card padding={true}>
                <div className="flex gap-3">
                    <div className="flex-1">
                        <Input
                            placeholder="Buscar descrição..."
                            value={filters.search}
                            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                            icon={MagnifyingGlass}
                        />
                    </div>
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                        className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                        <option value="">Todos</option>
                        <option value="pending">Pendentes</option>
                        <option value="received">Recebidos</option>
                    </select>
                </div>
            </Card>

            {/* Lista */}
            <Card padding={false}>
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto"></div>
                    </div>
                ) : incomes.length === 0 ? (
                    <div className="text-center py-12 px-6">
                        <TrendUp size={48} className="mx-auto mb-4 text-gray-600" />
                        <h3 className="text-lg font-semibold text-white mb-2">Nenhuma receita</h3>
                        <p className="text-gray-400 mb-4">Registre sua primeira receita</p>
                        <Button icon={Plus} onClick={openCreateModal}>Nova Receita</Button>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-700">
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Descrição</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Valor</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Categoria</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Previsto</th>
                                    <th className="text-left p-4 text-sm font-medium text-gray-400">Status</th>
                                    <th className="text-right p-4 text-sm font-medium text-gray-400">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {incomes.map((income) => (
                                    <tr key={income.id} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                                        <td className="p-4">
                                            <div>
                                                <p className="text-white font-medium">{income.description}</p>
                                                {income.recurring && (
                                                    <p className="text-xs text-emerald-500 mt-0.5">
                                                        🔄 Recorrente ({income.recurrence_type === 'monthly' ? 'Mensal' :
                                                            income.recurrence_type === 'weekly' ? 'Semanal' : 'Anual'})
                                                    </p>
                                                )}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span className="text-white font-medium">{formatCurrency(income.amount)}</span>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-2">
                                                <div
                                                    className="w-3 h-3 rounded-full"
                                                    style={{ backgroundColor: income.category_color }}
                                                />
                                                <span className="text-gray-300 text-sm">{income.category_name}</span>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-2">
                                                <Calendar size={16} className="text-gray-400" />
                                                <span className="text-gray-300 text-sm">{formatDate(income.expected_date)}</span>
                                            </div>
                                        </td>
                                        <td className="p-4">{getStatusBadge(income.status)}</td>
                                        <td className="p-4">
                                            <div className="flex items-center justify-end gap-1">
                                                {income.status === 'pending' && (
                                                    <button
                                                        onClick={() => handleReceive(income.id)}
                                                        className="p-2 hover:bg-emerald-500/20 rounded-lg text-gray-400 hover:text-emerald-500"
                                                        title="Marcar como recebido"
                                                    >
                                                        <CheckCircle size={18} />
                                                    </button>
                                                )}
                                                <button
                                                    onClick={() => handleDelete(income.id)}
                                                    className="p-2 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-500"
                                                    title="Excluir"
                                                >
                                                    <Trash size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>

            {/* Modal Nova Receita */}
            <Modal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                title="Nova Receita"
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-500/10 border border-red-500 text-red-500 rounded-lg p-3 text-sm">
                            {error}
                        </div>
                    )}

                    <Input
                        label="Descrição"
                        placeholder="Ex: Salário, Freelance..."
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                    />

                    <div className="grid grid-cols-2 gap-4">
                        <Input
                            label="Valor"
                            type="number"
                            step="0.01"
                            placeholder="5000.00"
                            value={formData.amount}
                            onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                            required
                        />
                        <Input
                            label="Data Prevista"
                            type="date"
                            value={formData.expected_date}
                            onChange={(e) => setFormData({ ...formData, expected_date: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">Categoria</label>
                        <select
                            value={formData.category_id}
                            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                            required
                        >
                            <option value="">Selecione</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            checked={formData.recurring}
                            onChange={(e) => setFormData({ ...formData, recurring: e.target.checked })}
                            className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-emerald-500 focus:ring-emerald-500"
                        />
                        <span className="text-gray-300">Receita Recorrente</span>
                    </div>

                    {formData.recurring && (
                        <select
                            value={formData.recurrence_type || ''}
                            onChange={(e) => setFormData({ ...formData, recurrence_type: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                        >
                            <option value="">Frequência</option>
                            <option value="weekly">Semanal</option>
                            <option value="monthly">Mensal</option>
                            <option value="yearly">Anual</option>
                        </select>
                    )}

                    <Input
                        label="Observações"
                        placeholder="Notas adicionais..."
                        value={formData.notes}
                        onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    />

                    <div className="flex gap-3 pt-4">
                        <Button type="submit" className="flex-1">Criar Receita</Button>
                        <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
                            Cancelar
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}