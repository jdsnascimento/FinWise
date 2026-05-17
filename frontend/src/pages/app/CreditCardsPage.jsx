import { Plus } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function CreditCardsPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Cartões de Crédito</h1>
                    <p className="text-gray-400 mt-1">Gerencie seus cartões</p>
                </div>
                <Button icon={Plus}>Novo Cartão</Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Card placeholder */}
                <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 text-white">
                    <div className="flex justify-between items-start mb-8">
                        <div>
                            <p className="text-sm opacity-80">Nubank</p>
                            <p className="text-lg font-bold">Mastercard</p>
                        </div>
                        <span className="text-2xl">💳</span>
                    </div>
                    <div>
                        <p className="text-sm opacity-80">Limite disponível</p>
                        <p className="text-2xl font-bold">R$ 4.200,00</p>
                        <div className="mt-2 bg-white/20 rounded-full h-2">
                            <div className="bg-white rounded-full h-2" style={{ width: '58%' }} />
                        </div>
                        <p className="text-xs mt-1 opacity-80">58% utilizado</p>
                    </div>
                </div>

                {/* Add card button */}
                <button className="border-2 border-dashed border-gray-700 rounded-xl p-6 flex flex-col items-center justify-center text-gray-500 hover:border-emerald-500 hover:text-emerald-500 transition-colors min-h-[200px]">
                    <Plus size={32} />
                    <span className="mt-2 font-medium">Novo Cartão</span>
                </button>
            </div>
        </div>
    );
}