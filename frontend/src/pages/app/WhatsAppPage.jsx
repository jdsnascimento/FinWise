import { useState, useEffect } from 'react';
import {
    WhatsappLogo,
    QrCode,
    CheckCircle,
    XCircle,
    Phone,
    Info
} from '@phosphor-icons/react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Badge from '../../components/ui/Badge';
import { whatsappService } from '../../services/whatsapp.service';

export default function WhatsAppPage() {
    const [status, setStatus] = useState(null);
    const [qrcode, setQrcode] = useState(null);
    const [loading, setLoading] = useState(false);
    const [phoneNumber, setPhoneNumber] = useState('');
    const [testMessage, setTestMessage] = useState('');
    const [parsedResult, setParsedResult] = useState(null);

    useEffect(() => {
        checkStatus();
        const interval = setInterval(checkStatus, 10000); // Verificar a cada 10s
        return () => clearInterval(interval);
    }, []);

    const checkStatus = async () => {
        try {
            const result = await whatsappService.getStatus();
            setStatus(result);
        } catch (err) {
            console.error('Erro ao verificar status:', err);
        }
    };

    const handleCreateInstance = async () => {
        if (!phoneNumber) return;

        setLoading(true);
        try {
            await whatsappService.createInstance({
                instance_name: `finwise_${Date.now()}`,
                phone_number: phoneNumber
            });

            // Aguardar e buscar QR Code
            setTimeout(async () => {
                const qr = await whatsappService.getQrCode();
                setQrcode(qr.qrcode);
                checkStatus();
            }, 3000);
        } catch (err) {
            alert('Erro ao criar instância');
        } finally {
            setLoading(false);
        }
    };

    const handleTestParse = async () => {
        if (!testMessage) return;

        try {
            const result = await whatsappService.testParse(testMessage);
            setParsedResult(result);
        } catch (err) {
            alert('Erro ao testar mensagem');
        }
    };

    const getStatusBadge = (connectionStatus) => {
        const statusMap = {
            connected: { variant: 'success', label: 'Conectado', icon: CheckCircle },
            connecting: { variant: 'warning', label: 'Conectando...', icon: QrCode },
            disconnected: { variant: 'danger', label: 'Desconectado', icon: XCircle }
        };
        const s = statusMap[connectionStatus] || statusMap.disconnected;
        const Icon = s.icon;
        return (
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm
        ${connectionStatus === 'connected' ? 'bg-emerald-500/10 text-emerald-500' :
                    connectionStatus === 'connecting' ? 'bg-yellow-500/10 text-yellow-500' :
                        'bg-red-500/10 text-red-500'}`}
            >
                <Icon size={16} />
                <span>{s.label}</span>
            </div>
        );
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-white">WhatsApp</h1>
                <p className="text-gray-400 mt-1">Conecte seu WhatsApp para registrar gastos por mensagem</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Conexão WhatsApp */}
                <Card title="Conexão" icon={WhatsappLogo}>
                    <div className="space-y-4">
                        {status && (
                            <div className="flex items-center justify-between">
                                <span className="text-gray-400">Status:</span>
                                {getStatusBadge(status.connection_status)}
                            </div>
                        )}

                        {!qrcode && status?.connection_status !== 'connected' && (
                            <div className="space-y-3">
                                <Input
                                    label="Número do WhatsApp"
                                    placeholder="5511999999999"
                                    value={phoneNumber}
                                    onChange={(e) => setPhoneNumber(e.target.value)}
                                    icon={Phone}
                                />
                                <Button
                                    onClick={handleCreateInstance}
                                    loading={loading}
                                    className="w-full"
                                >
                                    Conectar WhatsApp
                                </Button>
                            </div>
                        )}

                        {qrcode && status?.connection_status !== 'connected' && (
                            <div className="text-center space-y-4">
                                <p className="text-gray-400">Escaneie o QR Code com seu WhatsApp</p>
                                <div className="bg-white p-4 rounded-lg inline-block">
                                    <img
                                        src={qrcode.startsWith('data:image') ? qrcode : `data:image/png;base64,${qrcode}`}
                                        alt="QR Code WhatsApp"
                                        className="w-64 h-64"
                                    />
                                </div>
                                <p className="text-sm text-gray-500">
                                    Abra o WhatsApp {'>'} Aparelhos Conectados {'>'} Conectar um aparelho
                                </p>
                            </div>
                        )}

                        {status?.connection_status === 'connected' && (
                            <div className="text-center py-8">
                                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <WhatsappLogo size={32} className="text-emerald-500" />
                                </div>
                                <h3 className="text-lg font-semibold text-white mb-2">WhatsApp Conectado!</h3>
                                <p className="text-gray-400">
                                    Envie mensagens para registrar seus gastos automaticamente
                                </p>
                            </div>
                        )}
                    </div>
                </Card>

                {/* Como Usar */}
                <Card title="Como Usar" icon={Info}>
                    <div className="space-y-4">
                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-3">📝 Formatos de mensagem aceitos:</h4>
                            <div className="space-y-3">
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "Paguei 150 mercado no Nubank 3x"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ Valor: R$150 | Categoria: Mercado | Cartão: Nubank | 3 parcelas
                                    </p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "Gastei 89.90 uber"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ Valor: R$89,90 | Categoria: Transporte
                                    </p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "Recebi 5000 salário"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ Tipo: Receita | Valor: R$5.000 | Categoria: Salário
                                    </p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "pix 150 jantar"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ Valor: R$150 | Método: PIX | Categoria: Alimentação
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-2">💡 Dicas:</h4>
                            <ul className="text-sm text-gray-400 space-y-2">
                                <li>• Inclua o valor sempre</li>
                                <li>• Mencione o cartão para compras parceladas</li>
                                <li>• Use "x" para indicar parcelas (3x, 10x)</li>
                                <li>• Para receitas, use "recebi" ou "salário"</li>
                            </ul>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Teste do Parser */}
            <Card title="🧪 Testar Reconhecimento de Mensagem" icon={Info}>
                <div className="space-y-4">
                    <div className="flex gap-3">
                        <Input
                            placeholder='Ex: Paguei 150 mercado no Nubank 3x'
                            value={testMessage}
                            onChange={(e) => setTestMessage(e.target.value)}
                            className="flex-1"
                        />
                        <Button onClick={handleTestParse}>Testar</Button>
                    </div>

                    {parsedResult && (
                        <div className="bg-gray-700 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-3">Resultado do Reconhecimento:</h4>
                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Tipo:</span>
                                    <Badge variant={parsedResult.type === 'income' ? 'success' : 'warning'}>
                                        {parsedResult.type === 'income' ? 'Receita' : 'Despesa'}
                                    </Badge>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Confiança:</span>
                                    <span className="text-white">{Math.round(parsedResult.confidence)}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Valor:</span>
                                    <span className="text-white font-medium">
                                        R$ {parsedResult.amount?.toFixed(2)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Descrição:</span>
                                    <span className="text-white">{parsedResult.description || '-'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Categoria:</span>
                                    <span className="text-white">{parsedResult.category_hint || '-'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Método:</span>
                                    <span className="text-white capitalize">
                                        {parsedResult.payment_method === 'credit_card' ? 'Crédito' : parsedResult.payment_method}
                                    </span>
                                </div>
                                {parsedResult.installments > 1 && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Parcelas:</span>
                                        <span className="text-white">{parsedResult.installments}x</span>
                                    </div>
                                )}
                                {parsedResult.card_hint && (
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Cartão:</span>
                                        <span className="text-white">{parsedResult.card_hint}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </Card>
        </div>
    );
}