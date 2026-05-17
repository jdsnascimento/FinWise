import { Link, useLocation } from 'react-router-dom';
import {
    ChartPieSlice,
    ArrowCircleDown,
    ArrowCircleUp,
    Plus
} from '@phosphor-icons/react';

export default function MobileNav() {
    const location = useLocation();

    const isActive = (path) => {
        if (path === '/dashboard') {
            return location.pathname === '/dashboard';
        }
        return location.pathname.startsWith(path);
    };

    return (
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 z-40 pb-safe">
            <nav className="flex items-center justify-around p-2">
                <Link
                    to="/dashboard"
                    className={`flex flex-col items-center p-2 rounded-lg transition-colors ${isActive('/dashboard') ? 'text-emerald-500' : 'text-gray-400'}`}
                >
                    <ChartPieSlice size={24} weight={isActive('/dashboard') ? 'fill' : 'regular'} />
                    <span className="text-[10px] mt-1 font-medium">Início</span>
                </Link>

                <Link
                    to="/bills"
                    className={`flex flex-col items-center p-2 rounded-lg transition-colors ${isActive('/bills') ? 'text-emerald-500' : 'text-gray-400'}`}
                >
                    <ArrowCircleDown size={24} weight={isActive('/bills') ? 'fill' : 'regular'} />
                    <span className="text-[10px] mt-1 font-medium">Pagar</span>
                </Link>

                <div className="relative -top-5">
                    <button className="bg-emerald-500 hover:bg-emerald-600 text-white p-3 rounded-full shadow-lg shadow-emerald-500/20 transition-transform hover:scale-105">
                        <Plus size={24} weight="bold" />
                    </button>
                </div>

                <Link
                    to="/incomes"
                    className={`flex flex-col items-center p-2 rounded-lg transition-colors ${isActive('/incomes') ? 'text-emerald-500' : 'text-gray-400'}`}
                >
                    <ArrowCircleUp size={24} weight={isActive('/incomes') ? 'fill' : 'regular'} />
                    <span className="text-[10px] mt-1 font-medium">Receber</span>
                </Link>

                <Link
                    to="/reports"
                    className={`flex flex-col items-center p-2 rounded-lg transition-colors ${isActive('/reports') ? 'text-emerald-500' : 'text-gray-400'}`}
                >
                    <ChartPieSlice size={24} weight={isActive('/reports') ? 'fill' : 'regular'} />
                    <span className="text-[10px] mt-1 font-medium">Relatórios</span>
                </Link>
            </nav>
        </div>
    );
}
