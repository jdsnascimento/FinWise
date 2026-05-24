import { useEffect, useState, useRef } from 'react';
import { Bell, Warning, Calendar, CreditCard, X } from '@phosphor-icons/react';
import { notificationService } from '../../services/notification.service';
import { formatCurrency, formatDate } from '../../utils/format';

export default function NotificationsDropdown() {
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState({ bills: [], alerts: [] });
    const [loading, setLoading] = useState(false);
    const dropdownRef = useRef(null);

    const totalCount = notifications.bills.length + notifications.alerts.length;

    const fetchNotifications = async () => {
        setLoading(true);
        try {
            const data = await notificationService.getAllNotifications();
            setNotifications(data);
        } catch (error) {
            console.error('Erro ao buscar notificações', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotifications();
        // Atualiza a cada 5 minutos
        const interval = setInterval(fetchNotifications, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    // Fechar dropdown ao clicar fora
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="relative p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
                <Bell size={20} />
                {totalCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                        {totalCount > 9 ? '9+' : totalCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl z-50 max-h-96 overflow-y-auto">
                    <div className="flex items-center justify-between p-4 border-b border-gray-700">
                        <h3 className="text-white font-semibold">Notificações</h3>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                        >
                            <X size={16} />
                        </button>
                    </div>

                    {loading && (
                        <div className="p-4 text-center text-gray-400 text-sm">Carregando...</div>
                    )}

                    {!loading && totalCount === 0 && (
                        <div className="p-8 text-center text-gray-500">
                            <Bell size={32} className="mx-auto mb-2 opacity-50" />
                            <p className="text-sm">Nenhuma notificação</p>
                        </div>
                    )}

                    {!loading && (
                        <div className="divide-y divide-gray-700">
                            {/* Contas a Vencer */}
                            {notifications.bills.length > 0 && (
                                <div className="p-3">
                                    <p className="text-xs font-semibold text-gray-400 uppercase mb-2">Vencimentos</p>
                                    {notifications.bills.map((notif) => (
                                        <div
                                            key={notif.bill_id}
                                            className={`flex items-start gap-3 p-2 rounded-lg mb-1 ${notif.urgency === 'high'
                                                ? 'bg-red-500/10 border border-red-500/20'
                                                : 'bg-yellow-500/10 border border-yellow-500/20'
                                                }`}
                                        >
                                            {notif.days_until_due <= 1 ? (
                                                <Warning size={18} className="text-red-500 mt-0.5" />
                                            ) : (
                                                <Calendar size={18} className="text-yellow-500 mt-0.5" />
                                            )}
                                            <div className="flex-1">
                                                <p className="text-sm text-white">{notif.description}</p>
                                                <div className="flex justify-between items-center mt-1">
                                                    <span className="text-xs text-gray-400">
                                                        Vence {formatDate(notif.due_date)}
                                                    </span>
                                                    <span className="text-sm font-semibold text-white">
                                                        {formatCurrency(notif.amount)}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* Alertas de Limite */}
                            {notifications.alerts.length > 0 && (
                                <div className="p-3">
                                    <p className="text-xs font-semibold text-gray-400 uppercase mb-2">Limite dos Cartões</p>
                                    {notifications.alerts.map((alert) => (
                                        <div
                                            key={alert.card_id}
                                            className={`flex items-start gap-3 p-2 rounded-lg mb-1 ${alert.level === 'critical'
                                                ? 'bg-red-500/10 border border-red-500/20'
                                                : 'bg-yellow-500/10 border border-yellow-500/20'
                                                }`}
                                        >
                                            <CreditCard size={18} className={alert.level === 'critical' ? 'text-red-500 mt-0.5' : 'text-yellow-500 mt-0.5'} />
                                            <div className="flex-1">
                                                <p className="text-sm text-white">{alert.card_name}</p>
                                                <div className="flex justify-between items-center mt-1">
                                                    <span className="text-xs text-gray-400">
                                                        {alert.usage_percentage}% utilizado
                                                    </span>
                                                    <span className="text-sm font-semibold text-white">
                                                        {formatCurrency(alert.available_limit)} disponível
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {!loading && totalCount > 0 && (
                        <div className="p-3 border-t border-gray-700">
                            <button
                                onClick={() => setIsOpen(false)}
                                className="w-full text-center text-sm text-emerald-500 hover:text-emerald-400 py-1"
                            >
                                Fechar
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}