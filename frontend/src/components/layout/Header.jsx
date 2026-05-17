import { List, Bell, UserCircle } from '@phosphor-icons/react';
import { useAuth } from '../../contexts/AuthContext';
import { useState } from 'react';

export default function Header({ onMenuClick }) {
    const { user } = useAuth();
    const [showNotifications, setShowNotifications] = useState(false);

    return (
        <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4 lg:px-6">
            {/* Botão menu mobile */}
            <button
                onClick={onMenuClick}
                className="lg:hidden p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400"
            >
                <List size={24} />
            </button>

            {/* Espaço para breadcrumb ou busca */}
            <div className="flex-1" />

            {/* Ações */}
            <div className="flex items-center gap-2">
                {/* Notificações */}
                <div className="relative">
                    <button
                        onClick={() => setShowNotifications(!showNotifications)}
                        className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 relative"
                    >
                        <Bell size={20} />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full" />
                    </button>
                </div>

                {/* Perfil */}
                <div className="flex items-center gap-3 pl-4 border-l border-gray-700">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-white">{user?.name}</p>
                        <p className="text-xs text-gray-400">{user?.email}</p>
                    </div>
                    <div className="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center">
                        <UserCircle size={20} className="text-emerald-500" />
                    </div>
                </div>
            </div>
        </header>
    );
}