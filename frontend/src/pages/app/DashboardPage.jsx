import { useState, useEffect } from 'react';
import {
    Wallet,
    ArrowCircleDown,
    ArrowCircleUp,
    CreditCard,
    TrendUp,
    ChartPieSlice,
    Calendar,
    Warning,
    CheckCircle
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { dashboardService } from '../../services/dashboard.service';

export default function DashboardPage() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedMonth, setSelectedMonth] = useState(
        new Date().toISOString().slice(0, 7)
    );

    useEffect(() => {
        loadDashboard();
    }, [selectedMonth]);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const result = await dashboardService.getSummary(selectedMonth);
            setData(result);
        } catch (err) {
            console.error('Erro ao carregar dashboard:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value || 0);
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '';
        return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR');
    };

    const getMonthName = (monthStr) => {
        const [year, month] = monthStr.split('-');
        return new Date(year, month - 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-emerald-500 mx-auto"></div>
                    <p className="text-gray-400 mt-4">Carregando dashboard...</p>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const balancePositive = data.balance >= 0;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-1">
                        {getMonthName(data.current_month)}
                    </p>
                </div>
                <input
                    type="month"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                    className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
            </div>

            {/* Cards Principais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Saldo */}
                <Card padding={true} className="bg-gradient-to-br from-gray-800 to-gray-800/50">
                    <div className="flex items-start justify-between">
                        <div className={`p-3 rounded-xl ${balancePositive ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                            <Wallet size={24} className={balancePositive ? 'text-emerald-500' : 'text-red-500'} />
                        </div>
                    </div>
                    <div className="mt-4">
                        <p className="text-sm text-gray-400">Saldo do Mês</p>
                        <p className={`text-2xl font-bold mt-1 ${balancePositive ? 'text-emerald-500' : 'text-red-500'}`}>
                            {formatCurrency(data.balance)}
                        </p>
                    </div>
                </Card>

                {/* Receitas */}
                <Card padding={true}>
                    <div className="flex items-start justify-between">
                        <div className="p-3 rounded-xl bg-blue-500/20">
                            <ArrowCircleUp size={24} className="text-blue-500" />
                        </div>
                    </div>
                    <div className="mt-4">
                        <p className="text-sm text-gray-400">Receitas</p>
                        <p className="text-2xl font-bold text-white mt-1">{formatCurrency(data.total_income)}</p>
                    </div>
                </Card>

                {/* Despesas */}
                <Card padding={true}>
                    <div className="flex items-start justify-between">
                        <div className="p-3 rounded-xl bg-red-500/20">
                            <ArrowCircleDown size={24} className="text-red-500" />
                        </div>
                    </div>
                    <div className="mt-4">
                        <p className="text-sm text-gray-400">Despesas</p>
                        <p className="text-2xl font-bold text-white mt-1">{formatCurrency(data.total_expenses)}</p>
                        <div className="flex gap-2 mt-2 text-xs">
                            <Badge variant="success">Pagas {formatCurrency(data.paid_expenses)}</Badge>
                            <Badge variant="warning">Pendentes {formatCurrency(data.pending_expenses)}</Badge>
                        </div>
                    </div>
                </Card>

                {/* Cartões */}
                <Card padding={true}>
                    <div className="flex items-start justify-between">
                        <div className="p-3 rounded-xl bg-purple-500/20">
                            <CreditCard size={24} className="text-purple-500" />
                        </div>
                    </div>
                    <div className="mt-4">
                        <p className="text-sm text-gray-400">Cartões de Crédito</p>
                        <p className="text-2xl font-bold text-white mt-1">
                            {formatCurrency(data.credit_cards.available_limit)}
                        </p>
                        <div className="mt-2">
                            <div className="flex justify-between text-xs text-gray-400 mb-1">
                                <span>Limite utilizado</span>
                                <span>{data.credit_cards.usage_percentage}%</span>
                            </div>
                            <div className="bg-gray-700 rounded-full h-2">
                                <div
                                    className={`rounded-full h-2 transition-all ${data.credit_cards.usage_percentage > 80 ? 'bg-red-500' : 'bg-purple-500'
                                        }`}
                                    style={{ width: `${Math.min(data.credit_cards.usage_percentage, 100)}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Gráficos e Listas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gráfico de Barras - Comparativo Mensal */}
                <Card title="Comparativo Mensal" icon={ChartPieSlice}>
                    <div className="h-64">
                        <div className="flex items-end justify-between h-48 gap-2 px-2">
                            {data.monthly_comparison.map((month, idx) => {
                                const maxValue = Math.max(
                                    ...data.monthly_comparison.map(m => Math.max(m.income, m.expense))
                                );
                                const incomeHeight = maxValue > 0 ? (month.income / maxValue) * 100 : 0;
                                const expenseHeight = maxValue > 0 ? (month.expense / maxValue) * 100 : 0;

                                return (
                                    <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                                        <div className="w-full flex flex-col items-center gap-1" style={{ height: '160px' }}>
                                            {/* Barra de Receita */}
                                            <div className="w-full flex flex-col justify-end items-center" style={{ height: '50%' }}>
                                                <div
                                                    className="w-8 bg-blue-500 rounded-t"
                                                    style={{ height: `${incomeHeight}%`, minHeight: '2px' }}
                                                />
                                            </div>
                                            {/* Barra de Despesa */}
                                            <div className="w-full flex flex-col justify-end items-center" style={{ height: '50%' }}>
                                                <div
                                                    className="w-8 bg-red-500 rounded-t"
                                                    style={{ height: `${expenseHeight}%`, minHeight: '2px' }}
                                                />
                                            </div>
                                        </div>
                                        <span className="text-xs text-gray-500 mt-2">{month.month}</span>
                                    </div>
                                );
                            })}
                        </div>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-500 rounded" />
                                <span className="text-xs text-gray-400">Receitas</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-red-500 rounded" />
                                <span className="text-xs text-gray-400">Despesas</span>
                            </div>
                        </div>
                    </div>
                </Card>

                {/* Top Categorias */}
                <Card title="Top Categorias de Gastos" icon={TrendUp}>
                    <div className="space-y-4">
                        {data.top_categories.length === 0 ? (
                            <p className="text-gray-500 text-center py-8">Nenhum gasto no período</p>
                        ) : (
                            data.top_categories.map((cat, idx) => (
                                <div key={idx} className="space-y-2">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className="w-3 h-3 rounded-full"
                                                style={{ backgroundColor: cat.color }}
                                            />
                                            <span className="text-gray-300 text-sm">{cat.name}</span>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-white text-sm font-medium">
                                                {formatCurrency(cat.total)}
                                            </span>
                                            <span className="text-gray-500 text-xs w-12 text-right">
                                                {cat.percentage}%
                                            </span>
                                        </div>
                                    </div>
                                    <div className="bg-gray-700 rounded-full h-1.5">
                                        <div
                                            className="rounded-full h-1.5 transition-all"
                                            style={{
                                                width: `${cat.percentage}%`,
                                                backgroundColor: cat.color
                                            }}
                                        />
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </Card>
            </div>

            {/* Próximos Vencimentos */}
            <Card
                title="Próximos Vencimentos"
                icon={Calendar}
                action={
                    <button className="text-sm text-emerald-500 hover:text-emerald-400">
                        Ver todos
                    </button>
                }
            >
                {data.upcoming_bills.length === 0 ? (
                    <div className="text-center py-8">
                        <CheckCircle size={32} className="mx-auto mb-2 text-emerald-500" />
                        <p className="text-gray-400">Nenhuma conta a vencer! 🎉</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {data.upcoming_bills.map((bill) => {
                            const daysUntilDue = Math.ceil(
                                (new Date(bill.due_date) - new Date()) / (1000 * 60 * 60 * 24)
                            );
                            const isUrgent = daysUntilDue <= 3;

                            return (
                                <div
                                    key={bill.id}
                                    className={`flex items-center justify-between p-4 rounded-lg transition-colors ${isUrgent ? 'bg-red-500/10 border border-red-500/20' : 'bg-gray-700/30'
                                        }`}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-2 rounded-lg ${isUrgent ? 'bg-red-500/20' : 'bg-gray-600'}`}>
                                            {isUrgent ? (
                                                <Warning size={20} className="text-red-500" />
                                            ) : (
                                                <Calendar size={20} className="text-gray-400" />
                                            )}
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">{bill.description}</p>
                                            <div className="flex items-center gap-3 mt-0.5">
                                                {bill.card_name && (
                                                    <span className="text-xs text-gray-400">{bill.card_name}</span>
                                                )}
                                                {bill.installments && (
                                                    <span className="text-xs text-gray-500">{bill.installments}</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-white font-semibold">{formatCurrency(bill.amount)}</p>
                                        <p className={`text-xs mt-0.5 ${isUrgent ? 'text-red-500 font-medium' : 'text-gray-400'}`}>
                                            {daysUntilDue <= 0
                                                ? 'Vence hoje!'
                                                : daysUntilDue === 1
                                                    ? 'Amanhã'
                                                    : `${daysUntilDue} dias`}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </Card>
        </div>
    );
}