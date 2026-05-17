import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Layout
import AppLayout from './components/layout/AppLayout';

// Páginas públicas
import Login from './pages/Login';
import Register from './pages/Register';

// Páginas do app
import DashboardPage from './pages/app/DashboardPage';
import BillsPage from './pages/app/BillsPage';
import CreditCardsPage from './pages/app/CreditCardsPage';
import IncomesPage from './pages/app/IncomesPage';
import ReportsPage from './pages/app/ReportsPage';
import WhatsAppPage from './pages/app/WhatsAppPage';
import SettingsPage from './pages/app/SettingsPage';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Carregando...</p>
        </div>
      </div>
    );
  }

  return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Rotas públicas */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Rotas protegidas com layout */}
      <Route
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/bills" element={<BillsPage />} />
        <Route path="/credit-cards" element={<CreditCardsPage />} />
        <Route path="/incomes" element={<IncomesPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/whatsapp" element={<WhatsAppPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* Redirecionamentos */}
      <Route path="/" element={<Navigate to="/dashboard" />} />
      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}