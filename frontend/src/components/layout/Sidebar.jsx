import { Link, useLocation } from 'react-router-dom';
import {
    ChartPieSlice,
    CreditCard,
    Money,
    ArrowCircleDown,
    ArrowCircleUp,
    ChartBar,
    WhatsappLogo,
    Gear,
    SignOut
} from '@phosphor-icons/react';
import { useAuth } from '../../contexts/AuthContext';

const menuItems = [
    {
        section: 'Principal',
        items: [
            { path: '/dashboard', label: 'Dashboard', icon: ChartPieSlice },
            { path: '/credit-cards', label: 'Cartões', icon: CreditCard },
        ]
    },
    {
        section: 'Finanças',
        items: [
            { path: '/bills', label: 'Contas a Pagar', icon: ArrowCircleDown },
            { path: '/incomes', label: 'Contas a Receber', icon: ArrowCircleUp },
            { path: '/reports', label: 'Relatórios', icon: ChartBar },
        ]
    },
    {
        section: 'Configurações',
        items: [
            { path: '/whatsapp', label: 'WhatsApp', icon: WhatsappLogo },
            { path: '/settings', label: 'Configurações', icon: Gear },
        ]
    }
];

export default function Sidebar({ isOpen, onClose }) {
    const location = useLocation();
    const { logout } = useAuth();

    const isActive = (path) => {
        if (path === '/dashboard') {
            return location.pathname === '/dashboard';
        }
        return location.pathname.startsWith(path);
    };

    return (
        <>
            {/* Overlay mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <aside className={`
        fixed top-0 left-0 h-full w-64 bg-gray-900 border-r border-gray-800 z-50
        transform transition-transform duration-300 ease-in-out flex flex-col
        lg:translate-x-0 lg:static lg:z-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
                {/* Logo */}
                <div className="h-16 flex-shrink-0 flex items-center gap-3 px-6 border-b border-gray-800">
                    <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
                        <Money size={20} weight="bold" className="text-white" />
                    </div>
                    <span className="text-xl font-bold text-white">FinWise</span>
                </div>

                {/* Menu */}
                <nav className="flex-1 overflow-y-auto py-6 px-3">
                    {menuItems.map((section, idx) => (
                        <div key={idx} className="mb-6">
                            <h3 className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                {section.section}
                            </h3>
                            {section.items.map((item) => {
                                const Icon = item.icon;
                                const active = isActive(item.path);

                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        onClick={onClose}
                                        className={`
                      flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1
                      transition-all duration-200 group
                      ${active
                                                ? 'bg-emerald-500/10 text-emerald-500'
                                                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                            }
                    `}
                                    >
                                        <Icon size={20} weight={active ? 'fill' : 'regular'} />
                                        <span className="text-sm font-medium">{item.label}</span>
                                        {active && (
                                            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-500" />
                                        )}
                                    </Link>
                                );
                            })}
                        </div>
                    ))}
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-gray-800 bg-gray-900 flex-shrink-0">
                    <button
                        onClick={logout}
                        className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-white transition-all duration-200"
                    >
                        <SignOut size={20} />
                        <span className="text-sm font-medium">Sair</span>
                    </button>
                </div>
            </aside>
        </>
    );
}