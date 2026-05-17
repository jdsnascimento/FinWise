import { User, Bell } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';

export default function SettingsPage() {
    return (
        <div className="space-y-6 max-w-2xl">
            <div>
                <h1 className="text-2xl font-bold text-white">Configurações</h1>
                <p className="text-gray-400 mt-1">Gerencie sua conta e preferências</p>
            </div>

            <Card title="Dados Pessoais" icon={User}>
                <div className="space-y-4">
                    <Input label="Nome" defaultValue="João Silva" />
                    <Input label="Email" defaultValue="joao@email.com" type="email" />
                    <Input label="WhatsApp" defaultValue="5511999999999" />
                    <Button>Salvar Alterações</Button>
                </div>
            </Card>

            <Card title="Notificações" icon={Bell}>
                <div className="space-y-3">
                    {['Lembretes de vencimento', 'Alertas de limite', 'Resumo semanal'].map((item) => (
                        <label key={item} className="flex items-center justify-between py-2">
                            <span className="text-gray-300">{item}</span>
                            <input type="checkbox" defaultChecked className="toggle" />
                        </label>
                    ))}
                </div>
            </Card>
        </div>
    );
}