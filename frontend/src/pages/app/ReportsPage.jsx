import { useState, useEffect } from 'react';
import {
    ChartPieSlice,
    ChartBar,
    ChartLine,
    CreditCard,
    TrendUp,
    FilePdf,
    FileCsv,
    Calendar
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import { reportService } from '../../services/report.service';

export default function ReportsPage() {
    const [activeTab, setActiveTab] = useState('categories');
    const [period, setPeriod] = useState('month');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);

    useEffect(() => {
        loadReportData();
    }, [activeTab, period]);

    const getDateRange = () => {
        const today = new Date();
        const endDate = today.toISOString().split('T')[0];
        let startDate;

        switch (period) {
            case 'week':
                startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case 'month':
                startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                break;
            case 'year':
                startDate = new Date(today.getFullYear(), 0, 1);
                break;
            default:
                startDate = new Date(today.getFullYear(), today.getMonth(), 1);
        }

        return {
            start_date: startDate.toISOString().split('T')[0],
            end_date: endDate
        };
    };

    const loadReportData = async () => {
        setLoading(true);
        try {
            const { start_date, end_date } = getDateRange();
            let result;

            switch (activeTab) {
                case 'categories':
                    result = await reportService.byCategory(start_date, end_date);
                    break;
                case 'cards':
                    result = await reportService.byCard(start_date, end_date);
                    break;
                case 'evolution':
                    result = await reportService.monthlyEvolution(6);
                    break;
                case 'methods':
                    result = await reportService.paymentMethods(start_date, end_date);
                    break;
                default:
                    result = await reportService.fullReport(start_date, end_date);
            }
            setData(result);
        } catch (err) {
            console.error('Erro ao carregar relatório:', err);
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

    const tabs = [
        { id: 'categories', label: 'Categorias', icon: ChartPieSlice },
        { id: 'cards', label: 'Cartões', icon: CreditCard },
        { id: 'evolution', label: 'Evolução', icon: ChartLine },
        { id: 'methods', label: 'Pagamentos', icon: ChartBar },
    ];

    const periods = [
        { id: 'week', label: '7 dias' },
        { id: 'month', label: 'Mês' },
        { id: 'year', label: 'Ano' },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Relatórios</h1>
                    <p className="text-gray-400 mt-1">Análise detalhada das suas finanças</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="ghost" size="sm" icon={FilePdf}>
                        PDF
                    </Button>
                    <Button variant="ghost" size="sm" icon={FileCsv}>
                        CSV
                    </Button>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex flex-wrap gap-2">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${activeTab === tab.id
                                    ? 'bg-emerald-500 text-white'
                                    : 'bg-gray-800 text-gray-400 hover:text-white'
                                }`}
                        >
                            <Icon size={18} />
                            <span className="text-sm font-medium">{tab.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Filtro de período */}
            {activeTab !== 'evolution' && (
                <div className="flex gap-2">
                    {periods.map((p) => (
                        <button
                            key={p.id}
                            onClick={() => setPeriod(p.id)}
                            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${period === p.id
                                    ? 'bg-gray-700 text-white'
                                    : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            {p.label}
                        </button>
                    ))}
                </div>
            )}

            {/* Conteúdo */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {loading ? (
                    <div className="col-span-2 flex justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
                    </div>
                ) : (
                    <>
                        {/* Relatório por Categorias */}
                        {activeTab === 'categories' && data && (
                            <Card title="Gastos por Categoria" className="lg:col-span-2">
                                <div className="space-y-4">
                                    {data.length === 0 ? (
                                        <p className="text-gray-500 text-center py-8">Nenhum gasto no período</p>
                                    ) : (
                                        data.map((cat, idx) => (
                                            <div key={idx} className="space-y-2">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-3">
                                                        <div
                                                            className="w-4 h-4 rounded-full"
                                                            style={{ backgroundColor: cat.color }}
                                                        />
                                                        <span className="text-white font-medium">{cat.category}</span>
                                                        <Badge variant="default">{cat.count} transações</Badge>
                                                    </div>
                                                    <div className="flex items-center gap-4">
                                                        <span className="text-white font-semibold">
                                                            {formatCurrency(cat.total)}
                                                        </span>
                                                        <span className="text-gray-400 text-sm w-16 text-right">
                                                            {cat.percentage}%
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="bg-gray-700 rounded-full h-3">
                                                    <div
                                                        className="rounded-full h-3 transition-all"
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
                        )}

                        {/* Relatório por Cartões */}
                        {activeTab === 'cards' && data && (
                            <Card title="Gastos por Cartão" className="lg:col-span-2">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {data.length === 0 ? (
                                        <p className="text-gray-500 text-center col-span-2 py-8">
                                            Nenhum gasto com cartão no período
                                        </p>
                                    ) : (
                                        data.map((card, idx) => (
                                            <div
                                                key={idx}
                                                className="bg-gray-700/30 rounded-xl p-6"
                                                style={{ borderLeft: `4px solid ${card.color}` }}
                                            >
                                                <div className="flex items-center justify-between mb-4">
                                                    <div>
                                                        <h4 className="text-white font-semibold">{card.card_name}</h4>
                                                        <p className="text-sm text-gray-400">{card.flag}</p>
                                                    </div>
                                                    <Badge variant="info">{card.count} compras</Badge>
                                                </div>
                                                <p className="text-3xl font-bold text-white">
                                                    {formatCurrency(card.total)}
                                                </p>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </Card>
                        )}

                        {/* Evolução Mensal */}
                        {activeTab === 'evolution' && data && (
                            <Card title="Evolução Financeira" className="lg:col-span-2">
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-gray-700">
                                                <th className="text-left p-3 text-sm text-gray-400">Mês</th>
                                                <th className="text-right p-3 text-sm text-gray-400">Receitas</th>
                                                <th className="text-right p-3 text-sm text-gray-400">Despesas</th>
                                                <th className="text-right p-3 text-sm text-gray-400">Saldo</th>
                                                <th className="text-right p-3 text-sm text-gray-400">Economia</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {data.map((month, idx) => (
                                                <tr key={idx} className="border-b border-gray-700/50">
                                                    <td className="p-3 text-white">{month.month_name}</td>
                                                    <td className="p-3 text-right text-blue-400">
                                                        {formatCurrency(month.income)}
                                                    </td>
                                                    <td className="p-3 text-right text-red-400">
                                                        {formatCurrency(month.expense)}
                                                    </td>
                                                    <td className={`p-3 text-right font-medium ${month.balance >= 0 ? 'text-emerald-400' : 'text-red-400'
                                                        }`}>
                                                        {formatCurrency(month.balance)}
                                                    </td>
                                                    <td className="p-3 text-right">
                                                        <Badge variant={month.savings_rate >= 0 ? 'success' : 'danger'}>
                                                            {month.savings_rate}%
                                                        </Badge>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </Card>
                        )}

                        {/* Métodos de Pagamento */}
                        {activeTab === 'methods' && data && (
                            <Card title="Métodos de Pagamento" className="lg:col-span-2">
                                <div className="space-y-4">
                                    {data.map((method, idx) => (
                                        <div key={idx} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <Badge variant="info">{method.method_name}</Badge>
                                                    <span className="text-gray-400 text-sm">
                                                        {method.count} transações
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <span className="text-white font-semibold">
                                                        {formatCurrency(method.total)}
                                                    </span>
                                                    <span className="text-gray-400 text-sm w-16 text-right">
                                                        {method.percentage}%
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="bg-gray-700 rounded-full h-3">
                                                <div
                                                    className="bg-emerald-500 rounded-full h-3 transition-all"
                                                    style={{ width: `${method.percentage}%` }}
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </Card>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}