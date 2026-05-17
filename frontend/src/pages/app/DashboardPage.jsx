import { useState } from 'react';
import {
    ChartPieSlice,
    ArrowCircleDown,
    ArrowCircleUp,
    Wallet,
    CreditCard,
    TrendUp
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function DashboardPage() {
    const [period, setPeriod] = useState('current');

    const summaryCards = [
        {
            title: 'Saldo Atual',
            value: 'R$ 5.240,00',
            change: '+12.5%',
            positive: true,
            icon: Wallet,
            color: 'text-emerald-500',
            bgColor: 'bg-emerald-500/10'
        },
        {
            title: 'Receitas do Mês',
            value: 'R$ 8.500,00',
            change: '+8.2%',
            positive: true,
            icon: ArrowCircleUp,
            color: 'text-blue-500',
            bgColor: 'bg-blue-500/10'
        },
        {
            title: 'Despesas do Mês',
            value: 'R$ 3.260,00',
            change: '-3.1%',
            positive: false,
            icon: ArrowCircleDown,
            color: 'text-red-500',
            bgColor: 'bg-red-500/10'
        },
        {
            title: 'Limite Cartões',
            value: 'R$ 4.800,00',
            subtitle: 'de R$ 10.000,00',
            icon: CreditCard,
            color: 'text-purple-500',
            bgColor: 'bg-purple-500/10'
        }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-1">Visão geral das suas finanças</p>
                </div>
                <div className="flex gap-2">
                    {['Atual', 'Junho', 'Julho'].map((p) => (
                        <Button
                            key={p}
                            variant={period === p.toLowerCase() ? 'primary' : 'secondary'}
                            size="sm"
                            onClick={() => setPeriod(p.toLowerCase())}
                        >
                            {p}
                        </Button>
                    ))}
                </div>
            </div>

            {/* Cards de Resumo */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {summaryCards.map((card, idx) => {
                    const Icon = card.icon;
                    return (
                        <Card key={idx} padding={true}>
                            <div className="flex items-start justify-between">
                                <div className={`p-2 rounded-lg ${card.bgColor}`}>
                                    <Icon size={24} className={card.color} />
                                </div>
                                {card.change && (
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${card.positive
                                            ? 'bg-emerald-500/10 text-emerald-500'
                                            : 'bg-red-500/10 text-red-500'
                                        }`}>
                                        {card.change}
                                    </span>
                                )}
                            </div>
                            <div className="mt-4">
                                <p className="text-sm text-gray-400">{card.title}</p>
                                <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
                                {card.subtitle && (
                                    <p className="text-sm text-gray-500 mt-0.5">{card.subtitle}</p>
                                )}
                            </div>
                        </Card>
                    );
                })}
            </div>

            {/* Gráficos e Listas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Gráfico placeholder */}
                <Card title="Gastos por Categoria" icon={ChartPieSlice}>
                    <div className="h-64 flex items-center justify-center text-gray-500">
                        <div className="text-center">
                            <TrendUp size={48} className="mx-auto mb-2 opacity-50" />
                            <p>Gráfico em construção</p>
                        </div>
                    </div>
                </Card>

                {/* Próximos Vencimentos */}
                <Card
                    title="Próximos Vencimentos"
                    icon={ArrowCircleDown}
                    action={
                        <Button size="sm" variant="ghost">
                            Ver todos
                        </Button>
                    }
                >
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                                <div>
                                    <p className="text-sm font-medium text-white">Compra Mercado</p>
                                    <p className="text-xs text-gray-400">Cartão Nubank • 1/3</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm font-semibold text-white">R$ 500,00</p>
                                    <p className="text-xs text-gray-400">15/06/2024</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}