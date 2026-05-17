import { ChartBar } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';

export default function ReportsPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Relatórios</h1>
                <p className="text-gray-400 mt-1">Análise detalhada das suas finanças</p>
            </div>

            <Card>
                <div className="text-center py-12 text-gray-500">
                    <ChartBar size={48} className="mx-auto mb-2 opacity-50" />
                    <p>Relatórios em construção</p>
                </div>
            </Card>
        </div>
    );
}