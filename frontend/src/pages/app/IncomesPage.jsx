import { Plus } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function IncomesPage() {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Contas a Receber</h1>
                    <p className="text-gray-400 mt-1">Gerencie suas receitas</p>
                </div>
                <Button icon={Plus}>Nova Receita</Button>
            </div>

            <Card>
                <div className="text-center py-12 text-gray-500">
                    <p>Lista de receitas em construção</p>
                </div>
            </Card>
        </div>
    );
}