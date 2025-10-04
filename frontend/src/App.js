import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import '@/App.css';

// Components
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';
import Transactions from './components/Transactions';
import AIInsights from './components/AIInsights';
import PaymentFlow from './components/PaymentFlow';
import ImportTransactions from './components/ImportTransactions';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:5000";
const API = `${BACKEND_URL}/api`;

// ProtectedRoute wrapper
const ProtectedRoute = ({ element: Component, isAuthenticated, ...rest }) => {
  return isAuthenticated ? <Component {...rest} /> : <Navigate to="/" replace />;
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('spendsmart_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    setShowAuth(false);
    localStorage.setItem('spendsmart_user', JSON.stringify(userData));
    navigate('/dashboard'); // go straight to dashboard after login
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('spendsmart_user');
    navigate('/'); // back to landing page
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {!isAuthenticated ? (
        <>
          <LandingPage onGetStarted={() => setShowAuth(true)} />
          {showAuth && (
            <AuthModal
              isOpen={showAuth}
              onClose={() => setShowAuth(false)}
              onLogin={handleLogin}
            />
          )}
        </>
      ) : (
        <Routes>
          <Route
            path="/dashboard"
            element={<ProtectedRoute element={Dashboard} isAuthenticated={isAuthenticated} user={currentUser} onLogout={handleLogout} />}
          />
          <Route
            path="/analytics"
            element={<ProtectedRoute element={Analytics} isAuthenticated={isAuthenticated} user={currentUser} onLogout={handleLogout} />}
          />
          <Route
            path="/transactions"
            element={<ProtectedRoute element={Transactions} isAuthenticated={isAuthenticated} user={currentUser} onLogout={handleLogout} />}
          />
          <Route
            path="/insights"
            element={<ProtectedRoute element={AIInsights} isAuthenticated={isAuthenticated} user={currentUser} onLogout={handleLogout} />}
          />
          <Route
            path="/pay"
            element={<ProtectedRoute element={PaymentFlow} isAuthenticated={isAuthenticated} user={currentUser} onLogout={handleLogout} />}
          />
          <Route
            path="/import"
            element={
              <ProtectedRoute
                element={ImportTransactions}
                isAuthenticated={isAuthenticated}
                user={currentUser}
                onLogout={handleLogout}
                onImportComplete={() => navigate('/transactions')}
              />
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      )}
    </div>
  );
}

// Wrap App with BrowserRouter outside
export default function WrappedApp() {
  return (
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
}
