import { WhatsappLogo, QrCode } from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function WhatsAppPage() {
    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">WhatsApp</h1>
                <p className="text-gray-400 mt-1">Conecte seu WhatsApp para registrar gastos</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Conectar WhatsApp" icon={WhatsappLogo}>
                    <div className="text-center py-8">
                        <div className="w-48 h-48 bg-white rounded-lg mx-auto mb-4 flex items-center justify-center">
                            <QrCode size={120} className="text-gray-800" />
                        </div>
                        <p className="text-gray-400 mb-4">
                            Escaneie o QR Code com seu WhatsApp
                        </p>
                        <Button>Gerar QR Code</Button>
                    </div>
                </Card>

                <Card title="Como usar" icon={WhatsappLogo}>
                    <div className="space-y-4 text-gray-400">
                        <div className="flex gap-3">
                            <span className="text-emerald-500 font-bold">1.</span>
                            <p>Conecte seu WhatsApp escaneando o QR Code</p>
                        </div>
                        <div className="flex gap-3">
                            <span className="text-emerald-500 font-bold">2.</span>
                            <p>Envie mensagens como: "Paguei 150 mercado no Nubank 3x"</p>
                        </div>
                        <div className="flex gap-3">
                            <span className="text-emerald-500 font-bold">3.</span>
                            <p>O FinWise registra automaticamente na sua conta!</p>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}