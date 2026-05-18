import { useState, useEffect, useRef } from 'react';
import {
    WhatsappLogo,
    QrCode,
    CheckCircle,
    XCircle,
    Phone,
    Info,
    ArrowClockwise
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
    const [error, setError] = useState('');
    const [connectStep, setConnectStep] = useState(''); // '', 'creating', 'waiting_qr', 'scanning'
    const qrPollRef = useRef(null);
    const statusPollRef = useRef(null);

    useEffect(() => {
        checkStatus();
        // Poll status a cada 5s
        statusPollRef.current = setInterval(checkStatus, 5000);
        return () => {
            if (statusPollRef.current) clearInterval(statusPollRef.current);
            if (qrPollRef.current) clearInterval(qrPollRef.current);
        };
    }, []);

    const checkStatus = async () => {
        try {
            const result = await whatsappService.getStatus();
            setStatus(result);
            
            // Se conectou, limpar QR e parar de buscar
            if (result.status === 'open' || result.connection_status === 'connected') {
                setQrcode(null);
                setConnectStep('');
                if (qrPollRef.current) {
                    clearInterval(qrPollRef.current);
                    qrPollRef.current = null;
                }
            }
        } catch (err) {
            console.error('Erro ao verificar status:', err);
        }
    };

    const handleCreateInstance = async () => {
        if (!phoneNumber) {
            setError('Informe o número do WhatsApp');
            return;
        }

        // Limpar número (só dígitos)
        const cleanNumber = phoneNumber.replace(/\D/g, '');
        if (cleanNumber.length < 10) {
            setError('Número inválido. Use formato: 5565999999999');
            return;
        }

        setLoading(true);
        setError('');
        setConnectStep('creating');
        setQrcode(null);

        try {
            // Nome é definido pelo backend (estável por usuário)
            await whatsappService.createInstance({
                instance_name: 'auto',
                phone_number: cleanNumber
            });

            setConnectStep('waiting_qr');

            // Aguardar instância ser criada e buscar QR code com retry
            let attempts = 0;
            const maxAttempts = 15;

            const fetchQr = async () => {
                attempts++;
                try {
                    const qr = await whatsappService.getQrCode();
                    if (qr.qrcode) {
                        setQrcode(qr.qrcode);
                        setConnectStep('scanning');
                        return true;
                    }
                } catch (e) {
                    console.log(`QR tentativa ${attempts}...`);
                }
                return false;
            };

            // Primeiro try após 2s
            await new Promise(r => setTimeout(r, 2000));
            const gotQr = await fetchQr();
            
            if (!gotQr) {
                // Continuar tentando a cada 3s
                qrPollRef.current = setInterval(async () => {
                    attempts++;
                    if (attempts >= maxAttempts) {
                        clearInterval(qrPollRef.current);
                        qrPollRef.current = null;
                        setError('Não foi possível gerar o QR Code. Tente novamente.');
                        setConnectStep('');
                        return;
                    }
                    
                    const success = await fetchQr();
                    if (success) {
                        clearInterval(qrPollRef.current);
                        qrPollRef.current = null;
                    }
                }, 3000);
            }
        } catch (err) {
            console.error('Erro ao criar instância:', err);
            setError('Erro ao conectar. Verifique se o Docker está rodando.');
            setConnectStep('');
        } finally {
            setLoading(false);
        }
    };

    const handleRefreshQr = async () => {
        setLoading(true);
        try {
            const qr = await whatsappService.getQrCode();
            if (qr.qrcode) {
                setQrcode(qr.qrcode);
            } else {
                setError('QR Code não disponível. Tente reconectar.');
            }
        } catch (err) {
            setError('Erro ao buscar QR Code');
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

    const isConnected = status?.status === 'open' || status?.connection_status === 'connected';

    const getStatusBadge = () => {
        if (isConnected) {
            return (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-emerald-500/10 text-emerald-500">
                    <CheckCircle size={16} />
                    <span>Conectado</span>
                </div>
            );
        }

        if (connectStep === 'creating' || connectStep === 'waiting_qr') {
            return (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-yellow-500/10 text-yellow-500">
                    <QrCode size={16} className="animate-spin" />
                    <span>Conectando...</span>
                </div>
            );
        }

        if (connectStep === 'scanning') {
            return (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-blue-500/10 text-blue-500">
                    <QrCode size={16} />
                    <span>Aguardando leitura do QR</span>
                </div>
            );
        }

        return (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-red-500/10 text-red-500">
                <XCircle size={16} />
                <span>Desconectado</span>
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
                        {/* Status */}
                        <div className="flex items-center justify-between">
                            <span className="text-gray-400">Status:</span>
                            {getStatusBadge()}
                        </div>

                        {/* Erro */}
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        {/* Formulário de conexão (quando desconectado) */}
                        {!isConnected && !qrcode && (
                            <div className="space-y-3">
                                <Input
                                    label="Número do WhatsApp (com DDD do país)"
                                    placeholder="5565992849548"
                                    value={phoneNumber}
                                    onChange={(e) => {
                                        setPhoneNumber(e.target.value);
                                        setError('');
                                    }}
                                    icon={Phone}
                                />
                                <p className="text-xs text-gray-500">
                                    Digite seu próprio número com código do país (55) + DDD + número
                                </p>
                                <Button
                                    onClick={handleCreateInstance}
                                    loading={loading || connectStep === 'creating' || connectStep === 'waiting_qr'}
                                    className="w-full"
                                >
                                    {loading || connectStep ? 'Conectando...' : 'Conectar WhatsApp'}
                                </Button>
                            </div>
                        )}

                        {/* QR Code para escanear */}
                        {qrcode && !isConnected && (
                            <div className="text-center space-y-4">
                                <p className="text-gray-400">Escaneie o QR Code com seu WhatsApp</p>
                                <div className="bg-white p-4 rounded-lg inline-block">
                                    <img
                                        src={qrcode.startsWith('data:image') ? qrcode : `data:image/png;base64,${qrcode}`}
                                        alt="QR Code WhatsApp"
                                        className="w-64 h-64"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <p className="text-sm text-gray-500">
                                        Abra o WhatsApp {'>'} Aparelhos Conectados {'>'} Conectar um aparelho
                                    </p>
                                    <Button
                                        onClick={handleRefreshQr}
                                        variant="outline"
                                        size="sm"
                                        className="mx-auto"
                                    >
                                        <ArrowClockwise size={14} className="mr-1" />
                                        Atualizar QR Code
                                    </Button>
                                </div>
                            </div>
                        )}

                        {/* Conectado */}
                        {isConnected && (
                            <div className="text-center py-8">
                                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <WhatsappLogo size={32} className="text-emerald-500" />
                                </div>
                                <h3 className="text-lg font-semibold text-white mb-2">WhatsApp Conectado!</h3>
                                <p className="text-gray-400 mb-4">
                                    Envie mensagens para <strong>você mesmo</strong> no WhatsApp para registrar seus gastos
                                </p>
                                <div className="bg-gray-700/30 rounded-lg p-3 text-left">
                                    <p className="text-sm text-emerald-400 font-medium mb-1">💡 Como usar:</p>
                                    <p className="text-xs text-gray-400">
                                        Abra o WhatsApp, vá na conversa consigo mesmo (seu próprio número) e envie uma mensagem como:
                                    </p>
                                    <p className="text-xs text-emerald-300 font-mono mt-1">
                                        "Gastei 50 uber" ou "pendentes"
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </Card>

                {/* Como Usar */}
                <Card title="Como Usar" icon={Info}>
                    <div className="space-y-4">
                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-3">💸 Registrar Despesas:</h4>
                            <div className="space-y-3">
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "Paguei 150 mercado no Nubank 3x"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ R$150 | Mercado | Cartão Nubank | 3 parcelas
                                    </p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "Gastei 89.90 uber"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ R$89,90 | Transporte
                                    </p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-emerald-400 text-sm font-mono mb-1">
                                        "pix 150 jantar"
                                    </p>
                                    <p className="text-gray-500 text-xs">
                                        ✅ R$150 | PIX | Alimentação
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-3">💰 Registrar Receitas:</h4>
                            <div className="bg-gray-800 rounded p-3">
                                <p className="text-emerald-400 text-sm font-mono mb-1">
                                    "Recebi 5000 salário"
                                </p>
                                <p className="text-gray-500 text-xs">
                                    ✅ Receita | R$5.000 | Salário
                                </p>
                            </div>
                        </div>

                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-3">📋 Consultar:</h4>
                            <div className="space-y-2">
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-blue-400 text-sm font-mono mb-1">"pendentes"</p>
                                    <p className="text-gray-500 text-xs">📋 Ver contas a pagar pendentes</p>
                                </div>
                                <div className="bg-gray-800 rounded p-3">
                                    <p className="text-blue-400 text-sm font-mono mb-1">"ajuda"</p>
                                    <p className="text-gray-500 text-xs">❓ Ver todos os comandos</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-700/30 rounded-lg p-4">
                            <h4 className="text-white font-medium mb-2">💡 Dicas:</h4>
                            <ul className="text-sm text-gray-400 space-y-2">
                                <li>• Envie as mensagens <strong className="text-white">para você mesmo</strong> no WhatsApp</li>
                                <li>• Inclua o valor sempre</li>
                                <li>• Use "x" para parcelas (3x, 10x)</li>
                                <li>• Digite <strong className="text-white">"pendentes"</strong> para ver suas contas</li>
                                <li>• Digite <strong className="text-white">"ajuda"</strong> para ver todos os comandos</li>
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
                            onKeyDown={(e) => e.key === 'Enter' && handleTestParse()}
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