import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import MobileNav from './MobileNav';

export default function AppLayout() {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-gray-900 flex">
            <Sidebar
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
            />

            <div className="flex-1 flex flex-col min-h-screen w-full lg:w-auto pb-16 lg:pb-0 relative">
                <Header onMenuClick={() => setSidebarOpen(true)} />

                <main className="flex-1 overflow-auto p-4 lg:p-6 flex flex-col">
                    <div className="flex-1 mb-8">
                        <Outlet />
                    </div>
                    <Footer />
                </main>

                <MobileNav />
            </div>
        </div>
    );
}